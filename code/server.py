# server.py - 最简单的视频服务器
from flask import Flask, request, send_file
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
        'url': f'/video/{filename}'
    }


# 2. 视频播放接口
@app.route('/video/<filename>')
def get_video(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return {'error': '文件不存在'}, 404


# 3. 视频列表接口
@app.route('/videos')
def list_videos():
    files = os.listdir(UPLOAD_FOLDER)
    return {
        'videos': [
            {'name': f, 'url': f'/video/{f}'}
            for f in files if f.endswith('.mp4')
        ]
    }


if __name__ == '__main__':
    print("🚀 视频服务器启动: http://localhost:5000")
    print("📁 视频保存目录: ./videos/")
    print("\n可用接口:")
    print("  POST /upload    - 上传视频")
    print("  GET  /videos    - 查看视频列表")
    print("  GET  /video/xxx - 播放视频")
    app.run(debug=True, host='0.0.0.0', port=5000)