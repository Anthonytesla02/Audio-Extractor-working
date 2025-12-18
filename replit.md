# YouTube to MP3 API

## Overview
A REST API for converting YouTube videos to MP3 and managing a song library. Designed for deployment to Railway with a React frontend.

## Current State
Fully functional REST API with:
- YouTube URL extraction and MP3 conversion
- Song library management with CRUD operations
- Audio streaming endpoint
- CORS enabled for React frontend integration
- Consistent JSON response format

## Project Structure
```
/
├── app.py              # Main Flask application with API endpoints
├── models.py           # SQLAlchemy Song model
├── main.py             # App entry point
├── Procfile            # Railway deployment command
├── railway.json        # Railway configuration
├── requirements.txt    # Python dependencies
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
- Flask-CORS - Cross-origin support for React frontend
- yt-dlp - YouTube audio extraction
- psycopg2-binary - PostgreSQL adapter
- gunicorn - Production WSGI server

## API Endpoints
- `GET /api/health` - Health check
- `POST /api/convert` - Extract audio from YouTube URL
- `GET /api/songs` - List all saved songs
- `POST /api/songs` - Save converted song to library
- `GET /api/songs/<id>` - Get single song details
- `GET /api/songs/<id>/audio` - Stream song audio
- `DELETE /api/songs/<id>` - Delete song from library
- `GET /api/download/<file_id>` - Download converted file

## Response Format
All endpoints return consistent JSON:
```json
{
  "success": true|false,
  "data": {...} | null,
  "message": "..." | null
}
```

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Secret key for sessions
- `PORT` - Server port (set by Railway)

## Database
Uses PostgreSQL to store songs with the following fields:
- id, title, artist, duration, youtube_url, audio_data (binary), file_size, created_at

## Recent Changes
- December 18, 2025: Converted to REST API for Railway deployment with React frontend support
- December 18, 2025: Added CORS, consistent response format, health endpoint
- December 17, 2025: Initial YouTube to MP3 converter
