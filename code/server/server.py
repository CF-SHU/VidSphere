# server.py - 1.0版本
from flask import Flask, request, send_file, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 1. 视频上传接口
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return {'error': '没有视频文件'}, 400

    video_file = request.files['video']
    filename = f"video_{len(os.listdir(UPLOAD_FOLDER)) + 1}.mp4"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    video_file.save(filepath)

    return {
        'success': True,
        'filename': filename,
        'url': f'/video/{filename}',
        'download_url': f'/download/{filename}'  # 添加下载链接
    }


# 2. 视频播放接口
@app.route('/video/<filename>')
def get_video(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return {'error': '文件不存在'}, 404


# 3. 视频下载接口 - 新增功能
@app.route('/download/<filename>')
def download_video(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        # 添加 as_attachment=True 参数使浏览器下载文件而不是播放
        return send_file(filepath, as_attachment=True)
    return {'error': '文件不存在'}, 404


# 4. 视频列表接口
@app.route('/videos')
def list_videos():
    files = os.listdir(UPLOAD_FOLDER)
    return {
        'videos': [
            {
                'name': f,
                'url': f'/video/{f}',
                'download_url': f'/download/{f}'  # 添加下载链接
            }
            for f in files if f.endswith('.mp4')
        ]
    }


if __name__ == '__main__':
    print("视频服务器启动: http://localhost:5000")
    print("视频保存目录: ./videos/")
    print("\n可用接口:")

    app.run(debug=True, host='0.0.0.0', port=5000)
