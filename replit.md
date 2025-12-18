# MusicBox - Mobile Music Player

## Overview
A mobile-friendly music player app that allows users to download music from YouTube and save it to their personal library for offline playback.

## Current State
Fully functional mobile music player with:
- YouTube URL extraction and MP3 conversion
- Database storage for offline playback
- Music library with playback controls
- Mobile-first responsive design

## Project Structure
```
/
├── app.py              # Main Flask application with API endpoints
├── models.py           # SQLAlchemy Song model
├── main.py             # App entry point
├── templates/
│   ├── index.html      # Add Music page
│   └── library.html    # Library and player page
├── downloads/          # Temporary storage for conversion
└── replit.md           # This file
```

## How to Run
The application runs on port 5000 via gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Dependencies
- Flask & Flask-SQLAlchemy - Web framework and ORM
- yt-dlp - YouTube audio extraction
- psycopg2-binary - PostgreSQL adapter
- gunicorn - Production WSGI server

## Features
1. **YouTube Extraction**: Paste a YouTube URL to extract audio
2. **Save to Library**: Songs are saved to PostgreSQL database as binary data
3. **Offline Playback**: Play saved songs anytime from your library
4. **Music Player**: Full playback controls with progress bar, prev/next
5. **Mobile-First UI**: Designed for mobile devices with bottom navigation

## API Endpoints
- `GET /` - Add music page
- `GET /library` - Library and player page
- `POST /convert` - Extract audio from YouTube URL
- `POST /save-to-library` - Save converted song to database
- `GET /api/songs` - List all saved songs
- `GET /api/songs/<id>/audio` - Stream song audio
- `DELETE /api/songs/<id>` - Delete song from library

## Database
Uses PostgreSQL to store songs with the following fields:
- id, title, artist, duration, youtube_url, audio_data (binary), file_size, created_at

## Recent Changes
- December 18, 2025: Transformed into mobile music player with library and offline playback
- December 17, 2025: Initial YouTube to MP3 converter
