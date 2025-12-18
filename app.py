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
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

CORS(app, origins="*", supports_credentials=True)

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

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/songs')
def get_songs():
    from models import Song
    songs = Song.query.order_by(Song.created_at.desc()).all()
    return jsonify([song.to_dict() for song in songs])

@app.route('/api/songs/<int:song_id>')
def get_song(song_id):
    from models import Song
    song = Song.query.get_or_404(song_id)
    return jsonify(song.to_dict())

@app.route('/api/songs/<int:song_id>/audio')
def stream_song(song_id):
    from flask import send_file
    from models import Song
    song = Song.query.get_or_404(song_id)
    return send_file(
        io.BytesIO(song.audio_data),
        mimetype='audio/mpeg',
        download_name=f"{song.title}.mp3",
        as_attachment=False
    )

@app.route('/api/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    from models import Song
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/convert', methods=['POST'])
def convert():
    clean_old_files()
    
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'error': 'Please provide a YouTube URL'})
    
    if not is_valid_youtube_url(url):
        return jsonify({'success': False, 'error': 'Invalid YouTube URL format'})
    
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
                return jsonify({'success': False, 'error': 'Could not extract video information'})
            title = info.get('title', 'audio')
            artist = info.get('uploader', 'Unknown Artist')
            duration = info.get('duration', 0)
        
        mp3_path = output_path + '.mp3'
        
        if not os.path.exists(mp3_path):
            for ext in ['.webm', '.m4a', '.opus', '.ogg']:
                alt_path = output_path + ext
                if os.path.exists(alt_path):
                    os.rename(alt_path, mp3_path)
                    break
        
        if os.path.exists(mp3_path):
            safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
            return jsonify({
                'success': True,
                'file_id': file_id,
                'title': title,
                'artist': artist,
                'safe_title': safe_title,
                'duration': duration,
                'youtube_url': url
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to convert audio'})
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Video unavailable' in error_msg:
            return jsonify({'success': False, 'error': 'Video is unavailable or private'})
        elif 'age-restricted' in error_msg.lower():
            return jsonify({'success': False, 'error': 'Video is age-restricted'})
        else:
            return jsonify({'success': False, 'error': 'Failed to download video. Please check the URL.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'})

@app.route('/save-to-library', methods=['POST'])
def save_to_library():
    from models import Song
    
    data = request.get_json()
    file_id = data.get('file_id')
    title = data.get('title', 'Unknown')
    artist = data.get('artist', 'Unknown Artist')
    duration = data.get('duration', 0)
    youtube_url = data.get('youtube_url', '')
    
    if not file_id or not re.match(r'^[a-f0-9\-]+$', file_id):
        return jsonify({'success': False, 'error': 'Invalid file ID'})
    
    mp3_path = os.path.join(DOWNLOAD_FOLDER, file_id + '.mp3')
    
    if not os.path.exists(mp3_path):
        return jsonify({'success': False, 'error': 'File not found or expired'})
    
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
        
        return jsonify({'success': True, 'song': song.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to save: {str(e)}'})

@app.route('/download/<file_id>')
def download(file_id):
    if not re.match(r'^[a-f0-9\-]+$', file_id):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    mp3_path = os.path.join(DOWNLOAD_FOLDER, file_id + '.mp3')
    
    if not os.path.exists(mp3_path):
        return jsonify({'error': 'File not found or expired'}), 404
    
    title = request.args.get('title', 'audio')
    safe_title = re.sub(r'[^\w\s-]', '', title)[:50] + '.mp3'
    
    return send_file(
        mp3_path,
        as_attachment=True,
        download_name=safe_title,
        mimetype='audio/mpeg'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
