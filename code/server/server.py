# server.py - 尝试使用OpenCV生成缩略图
from flask import Flask, request, send_file, render_template, redirect, url_for
import os
import time
from datetime import datetime
from collections import deque
import io
import sys

# 使用绝对路径确保正确找到模板
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'ui')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'videos')
THUMBNAIL_FOLDER = os.path.join(BASE_DIR, 'thumbnails')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

# 存储连接信息的队列，最多保存100条记录
connection_history = deque(maxlen=100)

# 存储通知消息的队列，最多保存20条通知
notifications = deque(maxlen=20)

# 记录服务器启动时间
server_start_time = time.time()

# 尝试导入OpenCV
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw

    CV_AVAILABLE = True
    print("OpenCV 已成功导入")
except ImportError as e:
    CV_AVAILABLE = False
    print(f" OpenCV 导入失败: {e}")
    print("   将使用默认缩略图")
    from PIL import Image, ImageDraw


def add_notification(message, level='info'):
    """添加一条通知消息"""
    notification = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'level': level  # info, success, warning, error
    }
    notifications.append(notification)
    print(f"日志: {message}")



def generate_default_thumbnail(thumbnail_path, size=(320, 180)):
    """生成一个默认的缩略图（灰色背景+播放图标）"""
    try:
        img = Image.new('RGB', size, color=(230, 230, 230))
        d = ImageDraw.Draw(img)

        # 绘制播放图标
        icon_size = min(size) // 4
        x_center = size[0] // 2
        y_center = size[1] // 2

        # 三角形播放图标
        triangle = [
            (x_center - icon_size // 2, y_center - icon_size // 2),
            (x_center - icon_size // 2, y_center + icon_size // 2),
            (x_center + icon_size // 2, y_center)
        ]
        d.polygon(triangle, fill=(100, 100, 100))

        # 添加文字
        text = "视频预览"
        d.text((x_center, y_center + icon_size), text, fill=(150, 150, 150), anchor="mm")

        # 保存图片
        img.save(thumbnail_path, 'JPEG', quality=90)
        print(f"已生成默认缩略图: {thumbnail_path}")
        return True
    except Exception as e:
        print(f"生成默认缩略图失败: {e}")
        return False


# 全局请求处理钩子 - 记录所有连接
@app.before_request
def log_connection():
    # 记录连接信息
    conn_info = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'ip': request.remote_addr,
        'method': request.method,
        'endpoint': request.path,
        'user_agent': request.user_agent.string if request.user_agent else 'Unknown',
        'status': '200'  # 默认为200，实际状态码需要在响应后更新
    }

    # 不记录监控页面本身的访问，避免干扰
    if request.path != '/monitor' and request.path != '/favicon.ico':
        connection_history.append(conn_info)


# 更新响应状态码的钩子
@app.after_request
def update_connection_status(response):
    if connection_history and request.path != '/monitor':
        # 更新最后一条记录的状态码
        connection_history[-1]['status'] = str(response.status_code)
    return response


# 1. 首页重定向到监控页面
@app.route('/')
def index():
    return redirect(url_for('monitor'))


# 2. 监控页面（主页面）
@app.route('/monitor')
def monitor():
    # 处理清空记录的请求
    if request.args.get('clear') == '1':
        connection_history.clear()
        notifications.clear()
        add_notification("已清空所有连接记录和通知", "info")

    # 计算服务器运行时间
    uptime_seconds = int(time.time() - server_start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    uptime_str = f"{hours}小时{minutes}分"

    # 获取视频数量
    video_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.mp4')]

    # 将连接历史转换为列表（从最新到最旧）
    connections = list(connection_history)[::-1]

    # 将通知转换为列表（从最新到最旧）
    notification_list = list(notifications)[::-1]

    return render_template('monitor.html',
                           connections=connections,
                           notifications=notification_list,
                           video_count=len(video_files),
                           uptime=uptime_str,
                           update_time=datetime.now().strftime('%H:%M:%S')
                           )


# 3. 视频上传接口
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        add_notification("上传失败: 没有视频文件", "error")
        return {'error': '没有视频文件'}, 400

    video_file = request.files['video']
    if video_file.filename == '':
        add_notification("上传失败: 没有选择文件", "error")
        return {'error': '没有选择文件'}, 400

    # 生成文件名
    original_name = video_file.filename
    base_name = os.path.splitext(original_name)[0]
    ext = os.path.splitext(original_name)[1] or '.mp4'

    # 确保文件名唯一
    counter = 1
    new_filename = f"{base_name}{ext}"
    while os.path.exists(os.path.join(UPLOAD_FOLDER, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    filepath = os.path.join(UPLOAD_FOLDER, new_filename)

    try:
        video_file.save(filepath)
        file_size = os.path.getsize(filepath) // 1024  # KB

        # 添加上传成功通知
        ip_address = request.remote_addr
        add_notification(f"用户 {ip_address} 上传了视频: {new_filename} ({file_size}KB)", "success")

        # 生成缩略图
        thumbnail_filename = new_filename + '.jpg'
        thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename)

        print(f"📹 正在为 {new_filename} 生成缩略图...")
        if generate_video_thumbnail(filepath, thumbnail_path):
            add_notification(f"已生成缩略图: {thumbnail_filename}", "info")
        else:
            add_notification(f"缩略图生成失败，使用默认缩略图", "warning")

        return {
            'success': True,
            'filename': new_filename,
            'url': f'/video/{new_filename}',
            'download_url': f'/download/{new_filename}',
            'original_name': original_name
        }
    except Exception as e:
        add_notification(f"上传失败: {str(e)}", "error")
        return {'error': f'保存文件失败: {str(e)}'}, 500


# 4. 视频播放接口
@app.route('/video/<filename>')
def get_video(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        # 添加播放通知
        ip_address = request.remote_addr
        file_size = os.path.getsize(filepath) // 1024  # KB
        add_notification(f"用户 {ip_address} 正在播放视频: {filename} ({file_size}KB)", "info")

        return send_file(filepath)

    add_notification(f"播放失败: 文件 {filename} 不存在", "warning")
    return {'error': '文件不存在'}, 404


# 5. 视频下载接口
@app.route('/download/<filename>')
def download_video(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        # 添加下载通知
        ip_address = request.remote_addr
        file_size = os.path.getsize(filepath) // 1024  # KB
        add_notification(f"用户 {ip_address} 正在下载视频: {filename} ({file_size}KB)", "info")

        return send_file(filepath, as_attachment=True, download_name=filename)

    add_notification(f"下载失败: 文件 {filename} 不存在", "warning")
    return {'error': '文件不存在'}, 404


# 6. 视频列表接口
@app.route('/videos')
def list_videos():
    files = os.listdir(UPLOAD_FOLDER)
    video_files = [f for f in files if f.endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'))]
    video_count = len(video_files)

    # 添加查看列表通知
    ip_address = request.remote_addr
    add_notification(f"用户 {ip_address} 查看了视频列表 (共{video_count}个视频)", "info")

    videos_list = []
    for f in video_files:
        # 检查缩略图是否存在
        thumbnail_filename = f + '.jpg'
        thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename)

        # 如果缩略图不存在，尝试生成
        if not os.path.exists(thumbnail_path):
            video_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.exists(video_path):
                print(f"为现有视频 {f} 生成缩略图...")
                if not generate_video_thumbnail(video_path, thumbnail_path):
                    # 确保至少有一个默认缩略图
                    generate_default_thumbnail(thumbnail_path)

        # 获取文件大小
        file_size_kb = 0
        try:
            file_size_kb = os.path.getsize(os.path.join(UPLOAD_FOLDER, f)) // 1024
        except:
            pass

        video_info = {
            'name': f,
            'author': '上传者',  # 可以根据需要修改
            'url': f'/video/{f}',
            'download_url': f'/download/{f}',
            'size': f"{file_size_kb}KB",
            'thumbnail': f'/preview/{f}'  # 缩略图URL
        }
        videos_list.append(video_info)

    return {'videos': videos_list}


# 7. 视频预览图接口
@app.route('/preview/<filename>')
def get_preview(filename):
    """
    获取视频预览图
    优先返回真实生成的缩略图，如果不存在则实时生成
    """
    # 确保文件名正确
    thumbnail_filename = filename + '.jpg'
    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename)

    # 如果缩略图存在，直接返回
    if os.path.exists(thumbnail_path):
        try:
            return send_file(thumbnail_path, mimetype='image/jpeg')
        except Exception as e:
            print(f"发送缩略图失败: {e}")

    # 如果缩略图不存在，尝试从视频生成
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(video_path):
        print(f" 实时生成缩略图: {filename}")
        if generate_video_thumbnail(video_path, thumbnail_path):
            return send_file(thumbnail_path, mimetype='image/jpeg')

    # 如果都失败，返回默认缩略图
    print(f"  使用默认缩略图: {filename}")

    # 在内存中生成默认缩略图
    img = Image.new('RGB', (320, 180), color=(230, 230, 230))
    d = ImageDraw.Draw(img)

    # 绘制播放图标
    d.polygon([(140, 70), (140, 110), (180, 90)], fill=(100, 100, 100))

    # 保存到内存
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=90)
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype='image/jpeg')


# 8. 生成所有视频的缩略图（手动触发）
@app.route('/generate_all_thumbnails')
def generate_all_thumbnails():
    """
    为所有现有视频生成缩略图
    """
    video_files = [f for f in os.listdir(UPLOAD_FOLDER) if
                   f.endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'))]
    success_count = 0
    fail_count = 0

    for video_file in video_files:
        thumbnail_filename = video_file + '.jpg'
        thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename)

        # 如果缩略图已存在，跳过
        if os.path.exists(thumbnail_path):
            continue

        video_path = os.path.join(UPLOAD_FOLDER, video_file)
        print(f" 为 {video_file} 生成缩略图...")

        if generate_video_thumbnail(video_path, thumbnail_path):
            success_count += 1
        else:
            fail_count += 1

    result_msg = f'已为 {success_count} 个视频生成缩略图，失败 {fail_count} 个'
    add_notification(result_msg, "info" if fail_count == 0 else "warning")

    return {
        'success': True,
        'message': result_msg,
        'success_count': success_count,
        'fail_count': fail_count
    }


# 9. 服务器状态接口
@app.route('/status')
def server_status():
    """获取服务器状态"""
    uptime_seconds = int(time.time() - server_start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60

    video_count = len(
        [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'))])
    thumbnail_count = len([f for f in os.listdir(THUMBNAIL_FOLDER) if f.endswith('.jpg')])

    return {
        'status': 'running',
        'uptime': f"{hours}小时{minutes}分",
        'video_count': video_count,
        'thumbnail_count': thumbnail_count,
        'opencv_available': CV_AVAILABLE,
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == '__main__':
    print(" 视频服务器启动")

    print(f"访问地址: http://localhost:5000")


    if not CV_AVAILABLE:


    # 添加初始通知
    add_notification("服务器已启动", "success")
    add_notification(f"OpenCV {'可用' if CV_AVAILABLE else '不可用'}", "info" if CV_AVAILABLE else "warning")

    # 导入socket用于获取本地IP
    import socket

    try:
        # 获取本机IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"局域网地址: http://{local_ip}:5000")
    except:
        pass

    app.run(debug=True, host='0.0.0.0', port=5000)
