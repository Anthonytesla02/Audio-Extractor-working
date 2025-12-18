# MusicBox - React Music Player

## Overview
A mobile-friendly music player app with a React frontend and Python Flask REST API backend. Users can download music from YouTube and save it to their personal library for offline playback.

## Architecture

### Frontend (React + Vite)
- Located in `/client` directory
- Runs on port 5000
- Uses React Router for navigation
- Proxy configuration to connect to backend API

### Backend (Flask REST API)
- Python Flask application with CORS enabled
- Runs on port 8000
- Ready for deployment to Render or similar platforms
- Uses PostgreSQL database (compatible with Neon.tech)

## Project Structure
```
/
├── client/                  # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── AddMusic.jsx    # YouTube URL input and conversion
│   │   │   ├── Library.jsx     # Music library with player
│   │   │   ├── Navigation.jsx  # Bottom navigation bar
│   │   │   └── Player.jsx      # Audio player component
│   │   ├── services/
│   │   │   └── api.js          # API service layer
│   │   ├── App.jsx             # Main app with routing
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── vite.config.js          # Vite configuration with proxy
│   └── package.json
├── app.py                   # Flask REST API
├── models.py                # SQLAlchemy Song model
├── main.py                  # App entry point
├── downloads/               # Temporary storage for conversion
└── replit.md                # This file
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/songs` | List all songs |
| GET | `/api/songs/:id` | Get single song |
| GET | `/api/songs/:id/audio` | Stream song audio |
| DELETE | `/api/songs/:id` | Delete song |
| POST | `/convert` | Convert YouTube URL to MP3 |
| POST | `/save-to-library` | Save converted song to library |
| GET | `/download/:file_id` | Download converted file |

## Features
1. **YouTube Extraction**: Paste a YouTube URL to extract audio
2. **Save to Library**: Songs are saved to PostgreSQL database as binary data
3. **Offline Playback**: Play saved songs anytime from your library
4. **Music Player**: Full playback controls with progress bar, prev/next
5. **Mobile-First UI**: Designed for mobile devices with bottom navigation

## Environment Variables

### Backend (for Render deployment)
- `DATABASE_URL` - PostgreSQL connection string (Neon.tech compatible)
- `SESSION_SECRET` - Secret key for Flask sessions

### Frontend (for production)
- `VITE_API_URL` - Backend API URL (set to your Render backend URL)

## Development

### Local Development
1. Backend runs on port 8000: `gunicorn --bind 0.0.0.0:8000 --reload main:app`
2. Frontend runs on port 5000: `cd client && npm run dev`
3. Vite proxies API calls to backend

### Production Deployment

#### Backend (Render)
1. Deploy Flask app to Render
2. Add PostgreSQL database (Render or Neon.tech)
3. Set environment variables: `DATABASE_URL`, `SESSION_SECRET`

#### Frontend
1. Build: `cd client && npm run build`
2. Set `VITE_API_URL` to your Render backend URL
3. Deploy `client/dist` as static site

## Recent Changes
- Dec 2024: Converted from server-rendered templates to React SPA
- Added CORS support for API
- Created reusable React components
- Implemented client-side audio player with React state management
