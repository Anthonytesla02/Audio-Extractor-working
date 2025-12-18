import os
import re
import time
import uuid
import logging
from flask import Flask, request, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import yt_dlp
import io

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

with app.app_context():
    import models
    db.create_all()


def api_response(data=None, message=None, success=True, status_code=200):
    response = {
        "success": success,
        "data": data,
        "message": message
    }
    return jsonify(response), status_code


def api_error(message, status_code=400):
    return api_response(data=None, message=message, success=False, status_code=status_code)


def is_valid_youtube_url(url):
    youtube_regex = re.compile(
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return youtube_regex.match(url) is not None


def clean_old_files():
    for filename in os.listdir(DOWNLOAD_FOLDER):
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        try:
            if os.path.isfile(filepath):
                file_age = time.time() - os.path.getmtime(filepath)
                if file_age > 3600:
                    os.remove(filepath)
        except:
            pass


@app.route('/api/health', methods=['GET'])
def health_check():
    return api_response(data={"status": "healthy"}, message="API is running")


@app.route('/api/songs', methods=['GET'])
def get_songs():
    from models import Song
    songs = Song.query.order_by(Song.created_at.desc()).all()
    return api_response(data=[song.to_dict() for song in songs])


@app.route('/api/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    from models import Song
    song = Song.query.get(song_id)
    if not song:
        return api_error("Song not found", 404)
    return api_response(data=song.to_dict())


@app.route('/api/songs/<int:song_id>/audio', methods=['GET'])
def stream_song(song_id):
    from models import Song
    song = Song.query.get(song_id)
    if not song:
        return api_error("Song not found", 404)
    return Response(
        io.BytesIO(song.audio_data),
        mimetype='audio/mpeg',
        headers={
            'Content-Length': str(len(song.audio_data)),
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'public, max-age=31536000'
        }
    )


@app.route('/api/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    from models import Song
    song = Song.query.get(song_id)
    if not song:
        return api_error("Song not found", 404)
    db.session.delete(song)
    db.session.commit()
    return api_response(message="Song deleted successfully")


@app.route('/api/convert', methods=['POST'])
def convert():
    clean_old_files()
    
    data = request.get_json()
    if not data:
        return api_error("Request body is required")
    
    url = data.get('url', '').strip()
    
    if not url:
        return api_error("Please provide a YouTube URL")
    
    if not is_valid_youtube_url(url):
        return api_error("Invalid YouTube URL format")
    
    try:
        file_id = str(uuid.uuid4())
        output_path = os.path.join(DOWNLOAD_FOLDER, file_id)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                return api_error("Could not extract video information")
            title = info.get('title', 'audio')
            artist = info.get('uploader', 'Unknown Artist')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')
        
        mp3_path = output_path + '.mp3'
        
        if not os.path.exists(mp3_path):
            for ext in ['.webm', '.m4a', '.opus', '.ogg']:
                alt_path = output_path + ext
                if os.path.exists(alt_path):
                    os.rename(alt_path, mp3_path)
                    break
        
        if os.path.exists(mp3_path):
            safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
            return api_response(data={
                'file_id': file_id,
                'title': title,
                'artist': artist,
                'safe_title': safe_title,
                'duration': duration,
                'youtube_url': url,
                'thumbnail': thumbnail
            }, message="Conversion successful")
        else:
            return api_error("Failed to convert audio", 500)
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Video unavailable' in error_msg:
            return api_error("Video is unavailable or private")
        elif 'age-restricted' in error_msg.lower():
            return api_error("Video is age-restricted")
        else:
            return api_error("Failed to download video. Please check the URL.")
    except Exception as e:
        logging.error(f"Conversion error: {str(e)}")
        return api_error(f"An error occurred: {str(e)}", 500)


@app.route('/api/songs', methods=['POST'])
def save_to_library():
    from models import Song
    
    data = request.get_json()
    if not data:
        return api_error("Request body is required")
    
    file_id = data.get('file_id')
    title = data.get('title', 'Unknown')
    artist = data.get('artist', 'Unknown Artist')
    duration = data.get('duration', 0)
    youtube_url = data.get('youtube_url', '')
    
    if not file_id or not re.match(r'^[a-f0-9\-]+$', file_id):
        return api_error("Invalid file ID")
    
    mp3_path = os.path.join(DOWNLOAD_FOLDER, file_id + '.mp3')
    
    if not os.path.exists(mp3_path):
        return api_error("File not found or expired", 404)
    
    try:
        with open(mp3_path, 'rb') as f:
            audio_data = f.read()
        
        song = Song(
            title=title,
            artist=artist,
            duration=duration,
            youtube_url=youtube_url,
            audio_data=audio_data,
            file_size=len(audio_data)
        )
        db.session.add(song)
        db.session.commit()
        
        os.remove(mp3_path)
        
        return api_response(data=song.to_dict(), message="Song saved to library", status_code=201)
    except Exception as e:
        logging.error(f"Save error: {str(e)}")
        return api_error(f"Failed to save: {str(e)}", 500)


@app.route('/api/download/<file_id>', methods=['GET'])
def download(file_id):
    if not re.match(r'^[a-f0-9\-]+$', file_id):
        return api_error("Invalid file ID")
    
    mp3_path = os.path.join(DOWNLOAD_FOLDER, file_id + '.mp3')
    
    if not os.path.exists(mp3_path):
        return api_error("File not found or expired", 404)
    
    title = request.args.get('title', 'audio')
    safe_title = re.sub(r'[^\w\s-]', '', title)[:50] + '.mp3'
    
    return send_file(
        mp3_path,
        as_attachment=True,
        download_name=safe_title,
        mimetype='audio/mpeg'
    )


@app.errorhandler(404)
def not_found(e):
    return api_error("Resource not found", 404)


@app.errorhandler(500)
def server_error(e):
    return api_error("Internal server error", 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
