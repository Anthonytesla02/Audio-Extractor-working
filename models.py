from app import db
from datetime import datetime

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    artist = db.Column(db.String(256), default='Unknown Artist')
    duration = db.Column(db.Integer, default=0)
    youtube_url = db.Column(db.String(512))
    audio_data = db.Column(db.LargeBinary, nullable=False)
    file_size = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'duration': self.duration,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
