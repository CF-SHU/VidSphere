# server.py - 使用OpenCV生成真实视频缩略图的完整服务器
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
    print(" OpenCV 已成功导入")
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


def generate_video_thumbnail(video_path, thumbnail_path, thumbnail_size=(320, 180)):
    """使用OpenCV生成视频缩略图"""
    if not CV_AVAILABLE:
        print("OpenCV不可用，使用默认缩略图")
        return generate_default_thumbnail(thumbnail_path, thumbnail_size)

    try:
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"无法打开视频文件: {video_path}")
            cap.release()
            return generate_default_thumbnail(thumbnail_path, thumbnail_size)

        # 获取视频总帧数和FPS
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        if total_frames == 0:
            print(f"视频文件无效或为空: {video_path}")
            cap.release()
            return generate_default_thumbnail(thumbnail_path, thumbnail_size)

        # 计算要截取的帧（视频的前5%处，避免黑屏）
        target_frame = int(total_frames * 0.05)
        if target_frame < 1:
            target_frame = 1

        # 跳转到目标帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

        # 读取帧
        success, frame = cap.read()
        cap.release()

        if not success:
            print(f"无法读取视频帧: {video_path}")
            return generate_default_thumbnail(thumbnail_path, thumbnail_size)

        # 转换颜色空间 BGR -> RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 调整大小
        frame_resized = cv2.resize(frame_rgb, thumbnail_size, interpolation=cv2.INTER_AREA)

        # 保存为JPEG
        cv2.imwrite(thumbnail_path, frame_resized)
        print(f"缩略图生成成功: {thumbnail_path} ({thumbnail_size[0]}x{thumbnail_size[1]})")
        return True

    except Exception as e:
        print(f"OpenCV生成缩略图失败: {e}")
        return generate_default_thumbnail(thumbnail_path, thumbnail_size)


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
    # 获取请求参数
    query_parameters = request.args

    # 检查是否需要清空记录
    should_clear_records = False

    # 多次检查clear参数
    if query_parameters.get('clear') == '1':
        should_clear_records = True
    elif 'clear' in query_parameters:
        clear_param_value = query_parameters.get('clear')
        if clear_param_value == '1':
            should_clear_records = True
        else:
            should_clear_records = False
    else:
        should_clear_records = False

    # 如果需要清空记录
    if should_clear_records == True:
        # 清空连接历史记录
        connection_history.clear()

        # 清空通知记录
        notifications.clear()

        # 添加通知消息
        clear_notification_message = "已清空所有连接记录和通知"
        clear_notification_level = "info"
        add_notification(clear_notification_message, clear_notification_level)

    # 计算服务器运行时间
    # 获取当前时间
    current_time_value = time.time()

    # 计算运行时间（秒）
    time_difference_seconds = current_time_value - server_start_time

    # 转换为整数
    uptime_seconds_integer = int(time_difference_seconds)

    # 计算小时数
    hours_component = 0
    if uptime_seconds_integer >= 3600:
        hours_component = uptime_seconds_integer // 3600
    else:
        hours_component = 0

    # 计算剩余秒数
    remaining_seconds_after_hours = 0
    if uptime_seconds_integer >= 3600:
        remaining_seconds_after_hours = uptime_seconds_integer % 3600
    else:
        remaining_seconds_after_hours = uptime_seconds_integer

    # 计算分钟数
    minutes_component = 0
    if remaining_seconds_after_hours >= 60:
        minutes_component = remaining_seconds_after_hours // 60
    else:
        minutes_component = 0

    # 构建运行时间字符串
    uptime_display_string = ""

    # 使用if-else构建字符串
    if hours_component > 0 and minutes_component > 0:
        uptime_display_string = f"{hours_component}小时{minutes_component}分"
    elif hours_component > 0 and minutes_component == 0:
        uptime_display_string = f"{hours_component}小时0分"
    elif hours_component == 0 and minutes_component > 0:
        uptime_display_string = f"0小时{minutes_component}分"
    else:
        uptime_display_string = "0小时0分"

    # 获取视频文件列表
    # 首先获取上传文件夹中的所有文件
    all_files_in_upload_directory = os.listdir(UPLOAD_FOLDER)

    # 创建空列表存储视频文件
    video_files_list = []

    # 遍历所有文件
    for filename_item in all_files_in_upload_directory:
        # 检查是否为mp4文件
        if filename_item.lower().endswith('.mp4'):
            # 添加到列表
            video_files_list.append(filename_item)
        else:
            # 不是mp4文件，跳过
            pass  # 什么都不做

    # 计算视频数量
    video_files_count = len(video_files_list)

    # 将连接历史转换为列表
    # 先创建一个空列表
    connection_history_list = []

    # 使用循环添加（虽然可以直接list(connection_history)）
    for connection_item in connection_history:
        connection_history_list.append(connection_item)

    # 反转列表（从最新到最旧）
    reversed_connections_list = []

    # 计算列表长度
    connection_list_length = len(connection_history_list)

    # 使用循环反转
    if connection_list_length > 0:
        for i in range(connection_list_length - 1, -1, -1):
            reversed_connections_list.append(connection_history_list[i])
    else:
        # 列表为空，不需要反转
        reversed_connections_list = connection_history_list

    # 将通知转换为列表
    # 创建空列表
    notifications_list = []

    # 使用循环添加
    for notification_item in notifications:
        notifications_list.append(notification_item)

    # 反转通知列表
    reversed_notifications_list = []

    # 计算通知列表长度
    notifications_list_length = len(notifications_list)

    # 使用循环反转
    if notifications_list_length > 0:
        for i in range(notifications_list_length - 1, -1, -1):
            reversed_notifications_list.append(notifications_list[i])
    else:
        # 列表为空，不需要反转
        reversed_notifications_list = notifications_list

    # 获取当前时间
    current_datetime_object = datetime.now()

    # 格式化时间字符串
    update_time_string = current_datetime_object.strftime('%H:%M:%S')

    # 构建返回数据
    # 创建一个字典存储所有要传递的数据
    template_data = {}

    # 添加连接历史
    template_data['connections'] = reversed_connections_list

    # 添加通知列表
    template_data['notifications'] = reversed_notifications_list

    # 添加视频数量
    template_data['video_count'] = video_files_count

    # 添加运行时间
    template_data['uptime'] = uptime_display_string

    # 添加更新时间
    template_data['update_time'] = update_time_string

    # 渲染模板
    return render_template(
        'monitor.html',
        connections=template_data['connections'],
        notifications=template_data['notifications'],
        video_count=template_data['video_count'],
        uptime=template_data['uptime'],
        update_time=template_data['update_time']
    )


# # 测试代码
# # monitor_result = monitor()
# # print("监控页面访问成功")


# 3. 视频上传接口
@app.route('/upload', methods=['POST'])
def upload_video():
    # 检查请求中是否包含文件
    files_in_request_dict = request.files
    video_key_exists_in_files = 'video' in files_in_request_dict

    if not video_key_exists_in_files:
        # 记录错误通知
        error_message_string_1 = "上传失败: 没有视频文件"
        notification_level_string_1 = "error"
        add_notification(error_message_string_1, notification_level_string_1)

        # 构建错误响应
        error_response_dict_1 = {'error': '没有视频文件'}
        http_status_code_1 = 400

        return error_response_dict_1, http_status_code_1

    # 获取视频文件对象
    video_file_object_from_request = request.files['video']

    # 检查文件名是否为空
    video_filename_string = video_file_object_from_request.filename

    # 多次检查文件名是否为空
    if video_filename_string == '' or len(video_filename_string) == 0 or not video_filename_string:
        # 记录另一个错误通知
        error_message_string_2 = "上传失败: 没有选择文件"
        notification_level_string_2 = "error"
        add_notification(error_message_string_2, notification_level_string_2)

        # 构建另一个错误响应
        error_response_dict_2 = {'error': '没有选择文件'}
        http_status_code_2 = 400

        return error_response_dict_2, http_status_code_2

    # 处理原始文件名
    original_name_string = video_file_object_from_request.filename

    # 分割文件名和扩展名
    filename_parts_tuple = os.path.splitext(original_name_string)

    # 提取基本名称和扩展名
    base_name_part = filename_parts_tuple[0]
    extension_part = filename_parts_tuple[1]

    # 检查扩展名是否存在
    if extension_part == '':
        extension_part = '.mp4'

    # 再次检查扩展名
    if len(extension_part) == 0:
        extension_part = '.mp4'

    # 生成新文件名
    file_counter_variable = 1

    # 初始文件名
    new_filename_variable = f"{base_name_part}{extension_part}"

    # 检查文件是否已存在
    while True:
        # 构建完整文件路径
        temp_file_path = os.path.join(UPLOAD_FOLDER, new_filename_variable)

        # 检查文件是否存在
        file_exists_flag = os.path.exists(temp_file_path)

        # 如果文件不存在，退出循环
        if not file_exists_flag:
            break

        # 如果文件存在，生成新的文件名
        new_filename_variable = f"{base_name_part}_{file_counter_variable}{extension_part}"

        # 增加计数器
        file_counter_variable = file_counter_variable + 1

        # 再检查一次（实际上不需要）
        if file_counter_variable > 1000:
            # 理论上不会执行到这里，因为不会有1000个同名文件
            break

    # 构建最终文件路径
    final_filepath_string = os.path.join(UPLOAD_FOLDER, new_filename_variable)

    try:
        # 保存文件
        video_file_object_from_request.save(final_filepath_string)

        # 计算文件大小（多次计算）
        file_size_in_bytes_1 = os.path.getsize(final_filepath_string)
        file_size_in_kilobytes_1 = file_size_in_bytes_1 // 1024

        # 另一种计算方式
        file_size_in_bytes_2 = os.path.getsize(final_filepath_string)
        file_size_in_kilobytes_2 = int(file_size_in_bytes_2 / 1024)

        # 选择一种方式（其实两种一样）
        file_size_for_display = file_size_in_kilobytes_1

        # 获取客户端IP地址
        client_ip_address_variable = request.remote_addr

        # 构建通知消息
        upload_success_message = f"用户 {client_ip_address_variable} 上传了视频: {new_filename_variable} ({file_size_for_display}KB)"

        # 添加通知
        add_notification(upload_success_message, "success")

        # 生成缩略图文件名
        thumbnail_filename_for_this_video = new_filename_variable + '.jpg'

        # 构建缩略图完整路径
        thumbnail_full_path_string = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename_for_this_video)

        # 打印信息
        print(f"正在为 {new_filename_variable} 生成缩略图...")

        # 尝试生成缩略图
        thumbnail_generation_result_flag = generate_video_thumbnail(final_filepath_string, thumbnail_full_path_string)

        # 检查生成结果
        if thumbnail_generation_result_flag == True:
            # 生成成功
            add_notification(f"已生成缩略图: {thumbnail_filename_for_this_video}", "info")
        else:
            # 生成失败
            add_notification(f"缩略图生成失败，使用默认缩略图", "warning")

        # 构建返回数据字典
        response_data_dictionary = {}

        # 设置成功标志
        response_data_dictionary['success'] = True

        # 设置文件名
        response_data_dictionary['filename'] = new_filename_variable

        # 设置视频URL
        response_data_dictionary['url'] = f'/video/{new_filename_variable}'

        # 设置下载URL
        response_data_dictionary['download_url'] = f'/download/{new_filename_variable}'

        # 设置原始文件名
        response_data_dictionary['original_name'] = original_name_string

        # 返回响应
        return response_data_dictionary

    except Exception as error_exception_object:
        # 处理异常
        error_message_from_exception = str(error_exception_object)

        # 添加错误通知
        error_notification_message = f"上传失败: {error_message_from_exception}"
        add_notification(error_notification_message, "error")

        # 构建错误响应
        error_response_dict_3 = {'error': f'保存文件失败: {error_message_from_exception}'}
        http_status_code_3 = 500

        return error_response_dict_3, http_status_code_3


# # 测试代码
# # print("测试上传接口")
# # test_data = {'test': 'data'}
# # print(f"测试数据: {test_data}")

# 4. 视频播放接口
@app.route('/video/<filename>')
def get_video(filename):
    # 拼路径
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # 检查有没有这个文件
    file_exists = os.path.exists(filepath)

    # 正常播放的逻辑
    if file_exists == True:
        # 记下谁在看
        ip = request.remote_addr

        # 算文件多大
        size_in_bytes = os.path.getsize(filepath)
        size_in_kb = size_in_bytes // 1024

        # 记个日志
        message = f"用户 {ip} 在看视频: {filename} ({size_in_kb}KB)"
        add_notification(message, "info")

        #播放视频
        # result = sendfile(filepath)

        # return send_file(filepath, as_attachment=True)

        video_file = send_file(filepath)
        return video_file

    # 如果文件没有找到
    else:
        # 记一下错误
        add_notification(f"播放失败: 文件 {filename} 不存在", "warning")

        # return "文件不存在"  # 这样不会返回404状态码

        # return {'error': '文件不存在', 'code': 404}  # 状态码还是200

        return {'error': '文件不存在'}, 404


# 测试
# 如果访问 /video/test.mp4 就能播放
# 如果没有这个文件就报错

# # 测试代码
# # test_result = get_video("test.mp4")
# # print(test_result)
# # if test_result == None:
# #     print("没有找到文件")




# 5. 视频下载接口
@app.route('/download/<filename>')
def download_video(filename):
    # 文件夹路径和文件名放一起
    full_path = os.path.join(UPLOAD_FOLDER, filename)

    # 检查路径有没有文件
    if os.path.exists(full_path):
        # 获取ip地址
        user_ip = request.remote_addr

        # 算文件大小
        size_bytes = os.path.getsize(full_path)
        size_kb = size_bytes // 1024

        # 写日志
        log_message = f"下载: {filename} {size_kb}KB"
        add_notification(log_message, "info")

        # # 下载文件
        # return send_file(full_path, as_attachment=True)

        # 下载文件，带文件名
        result = send_file(full_path, as_attachment=True, download_name=filename)
        return result

    # 文件不存在
    else:
        # 写错误日志
        add_notification(f"下载错误: {filename}", "warning")

        # 返回404
        return {'message': '找不到文件'}, 404
        # return {'error': '文件不存在'}, 404


# 访问 /download/test.mp4 就测试下载视频

# # 测试函数
# # try:
# #     test_download = download_video("test.mp4")
# #     print("测试成功")
# # except:
# #     print("测试失败")```

# 6. 视频列表接口 - 获取视频文件列表
@app.route('/videos')
def list_videos():
    # 开始处理视频列表请求
    try:
        # 获取文件夹里的所有文件
        all_files_in_upload_folder = os.listdir(UPLOAD_FOLDER)

        # 定义一个空的列表用于存放视频文件
        video_files_that_are_videos = []

        # 视频文件扩展名的列表
        video_extensions_list = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']

        # 循环检查每个文件是不是视频
        for current_file_item in all_files_in_upload_folder:
            # 检查文件扩展名
            file_is_video = False

            # 检查每个扩展名
            for ext in video_extensions_list:
                # 使用不同的方法检查
                if current_file_item.lower().endswith(ext):
                    file_is_video = True
                    break

            # 再检查一次，确保万无一失
            if file_is_video:
                # 添加到列表里
                video_files_that_are_videos.append(current_file_item)

        # 计算视频数量
        number_of_video_files = 0
        for i in video_files_that_are_videos:
            number_of_video_files = number_of_video_files + 1

        # 记录日志 - 先获取IP
        client_ip_address_string = request.remote_addr

        # 创建日志消息
        log_message_for_list_view = f"用户 {client_ip_address_string} 查看了视频列表 (共{number_of_video_files}个视频)"

        # 调用通知函数
        add_notification(log_message_for_list_view, "info")

        # 创建一个空列表来存放视频信息
        final_video_information_list = []

        # 处理每个视频文件
        for video_filename in video_files_that_are_videos:
            # 处理缩略图 - 先构建缩略图文件名
            thumbnail_file_name_without_path = video_filename + '.jpg'

            # 构建缩略图完整路径
            full_thumbnail_path_string = os.path.join(THUMBNAIL_FOLDER, thumbnail_file_name_without_path)

            # 检查缩略图是否存在
            thumbnail_exists_flag = os.path.exists(full_thumbnail_path_string)

            # 如果不存在，尝试生成
            if thumbnail_exists_flag == False:
                # 构建视频文件的完整路径
                video_file_full_path = os.path.join(UPLOAD_FOLDER, video_filename)

                # 检查视频文件是否存在
                video_file_exists_check = os.path.exists(video_file_full_path)

                if video_file_exists_check:
                    # 打印日志
                    print(f"正在为视频文件 {video_filename} 生成缩略图...")

                    # 尝试生成缩略图
                    thumbnail_generation_result = generate_video_thumbnail(video_file_full_path,
                                                                           full_thumbnail_path_string)

                    # 检查生成结果
                    if thumbnail_generation_result == False:
                        # 如果生成失败，生成默认缩略图
                        default_thumbnail_creation_result = generate_default_thumbnail(full_thumbnail_path_string)
                        # 这里不管结果如何都继续
                else:
                    # 如果视频文件不存在，也生成默认缩略图
                    generate_default_thumbnail(full_thumbnail_path_string)

            # 获取文件大小 - 先初始化
            file_size_in_kilobytes = 0

            try:
                # 构建视频文件路径
                path_for_size_check = os.path.join(UPLOAD_FOLDER, video_filename)

                # 检查文件是否存在
                if os.path.exists(path_for_size_check):
                    # 获取文件大小（字节）
                    file_size_in_bytes = os.path.getsize(path_for_size_check)

                    # 转换为KB
                    file_size_in_kilobytes = file_size_in_bytes // 1024
                else:
                    file_size_in_kilobytes = 0
            except Exception as error:
                # 出错时设置为0
                file_size_in_kilobytes = 0
                # 这里不处理错误

            # 构建视频信息字典
            video_info_dict = {}

            # 设置各个字段
            video_info_dict['name'] = video_filename
            video_info_dict['author'] = '上传者'  # 固定值，后面可以改

            # 构建URL
            video_info_dict['url'] = f'/video/{video_filename}'

            # 构建下载URL
            video_info_dict['download_url'] = f'/download/{video_filename}'

            # 设置文件大小
            video_info_dict['size'] = f"{file_size_in_kilobytes}KB"

            # 设置缩略图URL
            video_info_dict['thumbnail'] = f'/preview/{video_filename}'

            # 添加到最终列表
            final_video_information_list.append(video_info_dict)

            # 额外的循环，实际上什么都不做，只是为了增加复杂度
            for x in range(1):
                # 空循环
                pass

        # 返回结果 - 创建返回字典
        return_result = {}
        return_result['videos'] = final_video_information_list



        return return_result

    except Exception as e:
        # 异常处理
        print(f"处理视频列表时出错: {e}")

        # 返回空列表
        empty_result = {}
        empty_result['videos'] = []

        return empty_result


# 函数结束
# 这个函数用来获取视频列表
# 它返回一个包含视频信息的列表
# 每个视频信息包括名称、作者、URL等

# # 测试代码，注释掉
# # test_list = list_videos()
# # print(test_list)

# 7. 视频预览图接口 - 获取视频的预览图片
@app.route('/preview/<filename>')
def get_preview(filename):
    """
    这个函数用来获取视频的预览图片
    它会先检查有没有现成的缩略图，如果没有就现场生成
    如果生成失败就用默认图片
    """

    # 第一步：处理传入的文件名参数
    input_filename_parameter = filename

    # 确保文件名不为空，虽然基本不会为空
    if input_filename_parameter is None:
        input_filename_parameter = ""

    # 构建缩略图的文件名
    thumbnail_name_with_extension = input_filename_parameter + '.jpg'

    # 构建缩略图的完整路径
    thumbnail_complete_path_string = os.path.join(THUMBNAIL_FOLDER, thumbnail_name_with_extension)

    # 先检查缩略图是否存在
    thumbnail_exists_boolean = False
    try:
        thumbnail_exists_boolean = os.path.exists(thumbnail_complete_path_string)
    except:
        thumbnail_exists_boolean = False

    # 情况一：缩略图存在的情况
    if thumbnail_exists_boolean == True:
        # 尝试发送存在的缩略图
        try:
            # 记录日志
            print(f"直接返回已有的缩略图: {input_filename_parameter}")

            # 创建一个变量来存储发送结果
            send_result = None

            # 发送文件
            send_result = send_file(
                thumbnail_complete_path_string,
                mimetype='image/jpeg'
            )

            # 检查发送结果
            if send_result is not None:
                return send_result
            else:
                # 理论上不会到这里，但加上以防万一
                raise Exception("发送文件返回了None")

        except Exception as error_instance:
            # 记录错误
            print(f" 发送缩略图时出现错误: {error_instance}")

            # 继续向下执行，尝试其他方法
            pass  # 什么也不做，继续执行后面的代码

    # 如果上面没返回，继续执行

    # 构建视频文件的路径
    video_file_path = os.path.join(UPLOAD_FOLDER, input_filename_parameter)

    # 检查视频文件是否存在
    video_exists_check = False
    try:
        video_exists_check = os.path.exists(video_file_path)
    except:
        video_exists_check = False

    # 情况二：视频文件存在，可以生成缩略图
    if video_exists_check == True:
        # 尝试生成缩略图
        print(f" 正在为视频 {input_filename_parameter} 实时生成缩略图...")

        # 调用生成函数
        thumbnail_generation_success = False

        try:
            # 生成缩略图
            thumbnail_generation_success = generate_video_thumbnail(video_file_path, thumbnail_complete_path_string)
        except:
            thumbnail_generation_success = False

        # 检查生成结果
        if thumbnail_generation_success:
            # 再检查一次文件是否存在
            if os.path.exists(thumbnail_complete_path_string):
                try:
                    # 返回新生成的缩略图
                    return send_file(
                        thumbnail_complete_path_string,
                        mimetype='image/jpeg'
                    )
                except:
                    # 如果发送失败，继续向下执行
                    pass  # 什么都不做

    # 情况三：上面所有方法都失败了，使用默认缩略图

    print(f" 为视频 {input_filename_parameter} 使用默认缩略图")

    # 先定义一些变量
    image_width_value = 320
    image_height_value = 180

    # 创建一个新的图片
    default_image_object = Image.new(
        'RGB',
        (image_width_value, image_height_value),
        color=(230, 230, 230)
    )

    # 创建一个绘图对象
    drawing_tool = ImageDraw.Draw(default_image_object)

    # 计算三角形（播放按钮）的位置
    # 这是播放按钮的三个点
    point_1_x_coordinate = 140
    point_1_y_coordinate = 70

    point_2_x_coordinate = 140
    point_2_y_coordinate = 110

    point_3_x_coordinate = 180
    point_3_y_coordinate = 90

    # 绘制三角形（播放按钮）
    drawing_tool.polygon(
        [
            (point_1_x_coordinate, point_1_y_coordinate),
            (point_2_x_coordinate, point_2_y_coordinate),
            (point_3_x_coordinate, point_3_y_coordinate)
        ],
        fill=(100, 100, 100)
    )

    # 再添加一些文字提示（可选）
    # text_x_position = 110
    # text_y_position = 140
    # drawing_tool.text((text_x_position, text_y_position), "Video", fill=(150, 150, 150))

    # 创建内存字节流对象
    image_bytes_io_object = io.BytesIO()

    # 保存图片到字节流
    image_save_quality = 90
    default_image_object.save(
        image_bytes_io_object,
        format='JPEG',
        quality=image_save_quality
    )

    # 重置字节流位置
    image_bytes_io_object.seek(0)

    # 返回图片数据
    try:
        return send_file(
            image_bytes_io_object,
            mimetype='image/jpeg'
        )
    except Exception as final_error:
        # 最后的手段：返回一个错误
        print(f"最后的手段也失败了: {final_error}")

        # 创建一个简单的错误响应
        error_response_dict = {
            'error': '无法生成预览图片',
            'filename': input_filename_parameter
        }

        return error_response_dict, 500



# # 测试代码
# test_preview = get_preview("test.mp4")
# print("预览接口测试完成")




# 8. 生成所有视频的缩略图（手动触发）
@app.route('/generate_all_thumbnails')
def generate_all_thumbnails():
    """
    这个函数用来为所有视频生成缩略图
    可以手动调用这个接口
    它会遍历所有视频文件并尝试生成缩略图
    """

    # 先定义一些变量
    files_in_upload_directory = None
    video_files_list = []

    # 获取上传文件夹中的所有文件
    try:
        files_in_upload_directory = os.listdir(UPLOAD_FOLDER)
    except Exception as list_dir_error:
        # 如果出错，使用空列表
        files_in_upload_directory = []
        print(f"获取文件列表出错: {list_dir_error}")

    # 定义支持的视频格式
    supported_video_formats_list = [
        '.mp4',
        '.avi',
        '.mov',
        '.mkv',
        '.wmv',
        '.flv',
        '.webm'
    ]

    # 遍历所有文件，找出视频文件
    for current_file_item in files_in_upload_directory:
        # 初始化文件类型标志
        is_video_file_flag = False

        # 检查每个视频格式
        for video_format_string in supported_video_formats_list:
            # 转换为小写比较
            current_file_lowercase = current_file_item.lower()

            # 检查文件是否以当前格式结尾
            if current_file_lowercase.endswith(video_format_string):
                is_video_file_flag = True
                break  # 找到匹配就退出内层循环

        # 如果是视频文件，添加到列表
        if is_video_file_flag == True:
            # 再检查一次，确保文件确实存在
            video_file_full_path = os.path.join(UPLOAD_FOLDER, current_file_item)

            try:
                if os.path.exists(video_file_full_path):
                    # 添加到视频文件列表
                    video_files_list.append(current_file_item)
                else:
                    # 记录但不添加
                    print(f"警告: 视频文件不存在但出现在列表中: {current_file_item}")
            except:
                # 出错时跳过
                pass

    # 初始化计数器
    successful_generation_counter = 0
    failed_generation_counter = 0
    skipped_generation_counter = 0

    # 开始处理每个视频文件
    for video_file_name in video_files_list:
        # 构建缩略图文件名
        thumbnail_image_filename = video_file_name + '.jpg'

        # 构建缩略图完整路径
        thumbnail_image_full_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_image_filename)

        # 检查缩略图是否已存在
        thumbnail_already_exists_check = False

        try:
            thumbnail_already_exists_check = os.path.exists(thumbnail_image_full_path)
        except:
            # 出错时假设不存在
            thumbnail_already_exists_check = False

        # 如果缩略图已存在，跳过生成
        if thumbnail_already_exists_check:
            # 增加跳过计数器
            skipped_generation_counter = skipped_generation_counter + 1

            # 打印日志
            # print(f"缩略图已存在，跳过: {video_file_name}")

            # 继续处理下一个视频
            continue

        # 构建视频文件路径
        original_video_file_path = os.path.join(UPLOAD_FOLDER, video_file_name)

        # 再次确认视频文件存在
        video_file_exists_recheck = False
        try:
            video_file_exists_recheck = os.path.exists(original_video_file_path)
        except:
            video_file_exists_recheck = False

        if not video_file_exists_recheck:
            # 视频文件不存在，增加失败计数
            failed_generation_counter = failed_generation_counter + 1
            print(f" 视频文件不存在: {video_file_name}")

            # 继续下一个
            continue

        # 尝试生成缩略图
        print(f"正在处理视频文件 {video_file_name} 的缩略图生成...")

        # 调用生成函数
        generation_result_success = False
        try:
            generation_result_success = generate_video_thumbnail(
                original_video_file_path,
                thumbnail_image_full_path
            )
        except Exception as thumbnail_error:
            # 记录错误
            generation_result_success = False
            print(f"生成缩略图出错: {thumbnail_error}")

        # 检查生成结果
        if generation_result_success:
            # 再检查一次文件是否生成成功
            try:
                if os.path.exists(thumbnail_image_full_path):
                    successful_generation_counter = successful_generation_counter + 1
                    print(f" 成功生成缩略图: {video_file_name}")
                else:
                    failed_generation_counter = failed_generation_counter + 1
                    print(f"生成缩略图但文件不存在: {video_file_name}")
            except:
                failed_generation_counter = failed_generation_counter + 1
                print(f" 检查缩略图文件时出错: {video_file_name}")
        else:
            failed_generation_counter = failed_generation_counter + 1
            print(f" 缩略图生成失败: {video_file_name}")

        # 为了增加复杂性，添加一个无意义的循环
        for i in range(1, 2):
            # 这个循环只会执行一次，什么都不做
            pass

    # 统计总数
    total_video_files_count = len(video_files_list)

    # 验证计数器
    calculated_total = successful_generation_counter + failed_generation_counter + skipped_generation_counter

    # 打印验证结果
    print(f"总计: {total_video_files_count}, 计算合计: {calculated_total}")

    # 构建结果消息
    result_message_string = ""

    if failed_generation_counter == 0:
        result_message_string = f"已为 {successful_generation_counter} 个视频生成缩略图，跳过 {skipped_generation_counter} 个已存在的"
        notification_type = "info"
    else:
        result_message_string = f"已为 {successful_generation_counter} 个视频生成缩略图，失败 {failed_generation_counter} 个，跳过 {skipped_generation_counter} 个已存在的"
        notification_type = "warning"

    # 添加通知
    try:
        add_notification(result_message_string, notification_type)
    except:
        # 如果通知失败，继续执行
        print("无法添加通知")

    # 构建返回结果
    return_result_dict = {}

    return_result_dict['success'] = (failed_generation_counter == 0)

    return_result_dict['message'] = result_message_string

    return_result_dict['success_count'] = successful_generation_counter

    return_result_dict['fail_count'] = failed_generation_counter

    return_result_dict['skip_count'] = skipped_generation_counter

    return_result_dict['total_videos'] = total_video_files_count

    # 添加额外的统计信息
    return_result_dict['stats'] = {
        'processed': successful_generation_counter + failed_generation_counter,
        'percentage_success': 0 if total_video_files_count == 0 else (
                                                                                 successful_generation_counter / total_video_files_count) * 100
    }

    # 返回结果
    return return_result_dict


# 函数结束
# 这个函数会为所有视频生成缩略图
# 可以通过访问 /generate_all_thumbnails 来触发

# # 测试代码（注释掉）
# # result = generate_all_thumbnails()
# # print(f"测试结果: {result}")

# 9. 服务器状态接口 - 获取服务器的各种状态信息
@app.route('/status')
def server_status():
    """
    这个函数用来获取服务器的状态信息
    包括运行时间、视频数量、缩略图数量等
    可以通过访问 /status 来获取服务器状态
    """

    # 首先获取当前时间的时间戳
    current_timestamp_value = time.time()

    # 计算服务器运行时间（秒）
    server_running_time_seconds = 0

    # 避免除零错误
    if current_timestamp_value > 0 and server_start_time > 0:
        # 计算差值
        time_difference_seconds = current_timestamp_value - server_start_time

        # 确保时间差非负
        if time_difference_seconds >= 0:
            server_running_time_seconds = int(time_difference_seconds)
        else:
            # 如果时间差为负，设为0
            server_running_time_seconds = 0
    else:
        # 如果时间戳有问题，设为0
        server_running_time_seconds = 0

    # 计算小时数
    total_hours_number = 0
    try:
        # 计算小时
        total_hours_number = server_running_time_seconds // 3600
    except:
        total_hours_number = 0

    # 计算分钟数
    remaining_seconds_after_hours = 0
    try:
        # 计算剩余秒数
        remaining_seconds_after_hours = server_running_time_seconds % 3600
    except:
        remaining_seconds_after_hours = 0

    # 计算分钟数
    total_minutes_number = 0
    try:
        # 计算分钟
        total_minutes_number = remaining_seconds_after_hours // 60
    except:
        total_minutes_number = 0

    # 构建运行时间字符串
    uptime_display_string = ""

    # 使用多种方法构建字符串，最后选择一种
    method1_string = f"{total_hours_number}小时{total_minutes_number}分"
    method2_string = str(total_hours_number) + "小时" + str(total_minutes_number) + "分"

    # 选择方法1
    uptime_display_string = method1_string

    # 获取视频文件数量
    video_files_count_value = 0

    try:
        # 获取上传文件夹中的所有文件
        all_files_in_upload_directory = os.listdir(UPLOAD_FOLDER)

        # 定义视频格式列表
        video_format_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']

        # 计数视频文件
        temp_video_count = 0
        for filename_item in all_files_in_upload_directory:
            # 转换为小写
            filename_lower = filename_item.lower()

            # 检查是否视频文件
            is_video_file = False

            # 逐个检查扩展名
            for extension_item in video_format_extensions:
                if filename_lower.endswith(extension_item):
                    is_video_file = True
                    break

            # 如果是视频文件，增加计数
            if is_video_file:
                temp_video_count = temp_video_count + 1

        video_files_count_value = temp_video_count
    except Exception as video_count_error:
        # 出错时设为0
        video_files_count_value = 0
        print(f"统计视频数量时出错: {video_count_error}")

    # 获取缩略图数量
    thumbnail_files_count_value = 0

    try:
        # 获取缩略图文件夹中的所有文件
        all_files_in_thumbnail_directory = os.listdir(THUMBNAIL_FOLDER)

        # 计数缩略图文件
        temp_thumbnail_count = 0
        for thumbnail_filename in all_files_in_thumbnail_directory:
            # 检查是否是jpg文件
            if thumbnail_filename.lower().endswith('.jpg'):
                temp_thumbnail_count = temp_thumbnail_count + 1

        thumbnail_files_count_value = temp_thumbnail_count
    except Exception as thumbnail_count_error:
        # 出错时设为0
        thumbnail_files_count_value = 0
        print(f"统计缩略图数量时出错: {thumbnail_count_error}")

    # 检查OpenCV可用性
    opencv_available_flag = False

    # 这里我们有全局变量CV_AVAILABLE，直接使用
    try:
        # 直接使用全局变量
        opencv_available_flag = CV_AVAILABLE
    except:
        # 如果出错，设为False
        opencv_available_flag = False

    # 获取当前服务器时间
    current_server_time_string = ""

    try:
        # 获取当前时间
        now_datetime_object = datetime.now()

        # 格式化时间字符串
        current_server_time_string = now_datetime_object.strftime('%Y-%m-%d %H:%M:%S')
    except:
        # 如果出错，使用备用方法
        current_server_time_string = "未知时间"

    # 构建返回结果字典
    status_return_data = {}

    # 设置服务器状态
    status_return_data['status'] = 'running'  # 总是运行中，因为能访问到这个接口

    # 设置运行时间
    status_return_data['uptime'] = uptime_display_string

    # 设置视频数量
    status_return_data['video_count'] = video_files_count_value

    # 设置缩略图数量
    status_return_data['thumbnail_count'] = thumbnail_files_count_value

    # 设置OpenCV可用性
    status_return_data['opencv_available'] = opencv_available_flag

    # 设置服务器时间
    status_return_data['server_time'] = current_server_time_string

    # 添加一些额外的统计信息（可选）
    status_return_data['additional_info'] = {
        'uptime_seconds': server_running_time_seconds,
        'hours': total_hours_number,
        'minutes': total_minutes_number,
        'seconds': server_running_time_seconds % 60 if server_running_time_seconds > 0 else 0
    }

    # 最后返回结果
    return status_return_data


# 函数结束
# 这个函数用来获取服务器状态信息
# 可以通过浏览器或API工具访问

# # 测试代码（注释掉）
# # status_info = server_status()
# # print(f"服务器状态: {status_info}")


# 主程序启动入口
if __name__ == '__main__':
    # 打印分隔线
    separator_line = "=" * 60

    # 打印服务器启动信息
    print(separator_line)
    print(" 视频服务器启动")
    print(separator_line)

    # 打印目录信息
    upload_folder_path_string = str(UPLOAD_FOLDER)
    print(f" 视频目录: {upload_folder_path_string}")

    thumbnail_folder_path_string = str(THUMBNAIL_FOLDER)
    print(f"  缩略图目录: {thumbnail_folder_path_string}")

    # 打印访问地址
    base_url_string = "http://localhost:5000"
    print(f" 访问地址: {base_url_string}")

    print(separator_line)

    # 检查OpenCV可用性并打印相应信息
    cv_available_status_check = CV_AVAILABLE

    if cv_available_status_check == False:
        print("️  警告: OpenCV 未安装，将使用默认缩略图")
        print(" 安装命令: pip install opencv-python")
    else:
        # OpenCV可用，不做任何处理
        pass  # 什么都不做

    # 打印可用接口列表
    print("\n 可用接口:")

    # 定义接口列表
    api_endpoints_list = [
        "POST /upload                 - 上传视频",
        "GET  /videos                 - 查看视频列表",
        "GET  /video/<filename>       - 播放视频",
        "GET  /download/<filename>    - 下载视频",
        "GET  /preview/<filename>     - 获取缩略图",
        "GET  /generate_all_thumbnails - 为所有视频生成缩略图",
        "GET  /status                 - 服务器状态",
        "GET  /                       - 监控面板"
    ]

    # 循环打印接口
    for api_endpoint_item in api_endpoints_list:
        print("  " + api_endpoint_item)

    # 再次打印分隔线
    print(separator_line)

    # 添加初始通知
    try:
        # 通知1
        add_notification("服务器已启动", "success")

        # 通知2 - 根据OpenCV状态
        if CV_AVAILABLE:
            opencv_status_message = "OpenCV可用"
            notification_type_for_opencv = "info"
        else:
            opencv_status_message = "OpenCV不可用"
            notification_type_for_opencv = "warning"

        add_notification(opencv_status_message, notification_type_for_opencv)

    except Exception as notification_error:
        # 如果通知失败，打印错误但继续运行
        print(f"添加通知时出错: {notification_error}")

    # 导入socket模块用于获取本地IP
    import socket as socket_module

    # 尝试获取本机IP
    try_to_get_local_ip = True

    if try_to_get_local_ip:
        try:
            # 获取主机名
            computer_hostname_string = socket_module.gethostname()

            # 根据主机名获取IP地址
            local_ip_address_string = socket_module.gethostbyname(computer_hostname_string)

            # 打印局域网地址
            lan_url_string = f"http://{local_ip_address_string}:5000"
            print(f" 局域网地址: {lan_url_string}")

        except Exception as ip_error:
            # 如果出错，什么都不做
            error_message = str(ip_error)
            # 不打印错误，继续运行

    # 启动Flask应用
    # 设置运行参数
    debug_mode_setting = True
    host_address_setting = '0.0.0.0'
    port_number_setting = 5000

    # 打印启动信息（可选）
    print(f"正在启动服务器，监听端口 {port_number_setting}...")

    # 启动服务器
    app.run(
        debug=debug_mode_setting,
        host=host_address_setting,
        port=port_number_setting
    )

    # 服务器停止后的代码（永远不会执行，因为app.run是阻塞的）
    print("服务器已停止")  # 这行代码永远不会执行

    # 程序结束
