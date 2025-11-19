from flask import Flask, send_file, jsonify
import yt_dlp
import os
import hashlib
from pathlib import Path

app = Flask(__name__)
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def get_video_id(url):
    """Generate unique ID from URL"""
    return hashlib.md5(url.encode()).hexdigest()

@app.route('/download/<video_id>')
def serve_video(video_id):
    """Serve downloaded video"""
    video_path = DOWNLOAD_DIR / f"{video_id}.mp4"
    if video_path.exists():
        return send_file(video_path, mimetype='video/mp4')
    return jsonify({"error": "Video not found"}), 404

@app.route('/process', methods=['POST'])
def process_video():
    """Download video and return file info"""
    from flask import request
    data = request.json
    url = data.get('url')
    base_url = data.get('base_url', 'http://localhost:5000')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    video_id = get_video_id(url)
    video_path = DOWNLOAD_DIR / f"{video_id}.mp4"
    
    # Check if already downloaded
    if video_path.exists():
        return jsonify({
            "video_id": video_id,
            "url": f"{base_url}/download/{video_id}",
            "cached": True
        })
    
    # Download video
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(video_path),
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return jsonify({
            "video_id": video_id,
            "url": f"{base_url}/download/{video_id}",
            "cached": False
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
