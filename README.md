# YouTube to MP3 API

A REST API for converting YouTube videos to MP3 and managing a song library. Ready for deployment to Railway with Neon PostgreSQL.

## Quick Start

### Setup Neon Database

1. Sign up at [neon.tech](https://neon.tech)
2. Create a project and copy your connection string
3. Initialize your database:

```bash
export DATABASE_URL="postgresql://user:pass@ep-xxxx.us-east-1.neon.tech/dbname?sslmode=require"
python scripts/init_db.py
```

4. Test the connection:
```bash
python scripts/test_connection.py
```

See [NEON_SETUP.md](./NEON_SETUP.md) for detailed instructions.

## API Endpoints

### Health Check
```
GET /api/health
```
Returns API status.

### Convert YouTube Video
```
POST /api/convert
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "file_id": "uuid",
    "title": "Video Title",
    "artist": "Channel Name",
    "duration": 180,
    "youtube_url": "...",
    "thumbnail": "..."
  },
  "message": "Conversion successful"
}
```

### Save Song to Library
```
POST /api/songs
Content-Type: application/json

{
  "file_id": "uuid-from-convert",
  "title": "Song Title",
  "artist": "Artist Name",
  "duration": 180,
  "youtube_url": "..."
}
```

### Get All Songs
```
GET /api/songs
```

### Get Single Song
```
GET /api/songs/:id
```

### Stream Song Audio
```
GET /api/songs/:id/audio
```
Returns audio/mpeg stream for playback.

### Delete Song
```
DELETE /api/songs/:id
```

### Download Converted File
```
GET /api/download/:file_id?title=song-name
```

## Response Format

All endpoints return consistent JSON:
```json
{
  "success": true|false,
  "data": {...} | null,
  "message": "error or success message"
}
```

## Environment Variables

- `DATABASE_URL` - Neon PostgreSQL connection string (with `?sslmode=require`)
- `SESSION_SECRET` - Secret key for sessions (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `PORT` - Server port (automatically set by Railway, defaults to 5000)

## Local Development

```bash
# Set environment variables
export DATABASE_URL="postgresql://..."
export SESSION_SECRET="your-secret"

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run the server
python main.py
```

## Deployment to Railway

1. Push code to GitHub
2. Create new project in Railway
3. Connect GitHub repository
4. Add PostgreSQL database (or use Neon)
5. Set environment variables:
   - `DATABASE_URL`: Your Neon connection string
   - `SESSION_SECRET`: Generated secret key
6. Deploy!

Railway will automatically use the `Procfile` for deployment.

## React Frontend Integration

Example usage in a React app:

```javascript
const API_URL = "https://your-railway-app.up.railway.app";

// Convert YouTube URL to MP3
const convertVideo = async (url) => {
  const response = await fetch(`${API_URL}/api/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  
  const result = await response.json();
  if (result.success) {
    return result.data;
  }
  throw new Error(result.message);
};

// Save to library
const saveToLibrary = async (fileData) => {
  const response = await fetch(`${API_URL}/api/songs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fileData)
  });
  return response.json();
};

// Get all songs
const getSongs = async () => {
  const response = await fetch(`${API_URL}/api/songs`);
  const result = await response.json();
  return result.data || [];
};

// Stream audio
const getAudioUrl = (songId) => {
  return `${API_URL}/api/songs/${songId}/audio`;
};
```

## Database Schema

**song table**
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | Primary key |
| title | VARCHAR(256) | Required |
| artist | VARCHAR(256) | Default: 'Unknown Artist' |
| duration | INTEGER | Seconds |
| youtube_url | VARCHAR(512) | Original URL |
| audio_data | BYTEA | MP3 binary data |
| file_size | INTEGER | Bytes |
| created_at | TIMESTAMP | Auto-set to current time |

**Indexes:**
- `idx_song_created_at` - For sorting by creation date
- `idx_song_artist` - For filtering by artist
- `idx_song_youtube_url` - For duplicate detection

## Troubleshooting

**Connection Error with sslmode**
- Ensure your DATABASE_URL includes `?sslmode=require`
- Neon requires SSL connections

**Table Already Exists**
- This is normal if you've run `init_db.py` before
- The script uses `CREATE TABLE IF NOT EXISTS`

**Audio Playback Issues**
- Verify audio_data is stored in database with: `SELECT file_size FROM song LIMIT 1`
- Check Content-Length header in audio response

## Project Files

```
.
├── app.py              # Flask application with routes
├── models.py           # SQLAlchemy Song model
├── main.py             # Entry point
├── Procfile            # Railway deployment
├── railway.json        # Railway config
├── requirements.txt    # Python dependencies
├── NEON_SETUP.md       # Neon setup guide
├── scripts/
│   ├── schema.sql      # Database schema
│   ├── init_db.py      # Initialize database
│   └── test_connection.py  # Test DB connection
└── README.md           # This file
```
