# YouTube to MP3 API

A REST API for converting YouTube videos to MP3 and managing a song library.

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
**Response:**
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
Returns audio stream (audio/mpeg).

### Delete Song
```
DELETE /api/songs/:id
```

### Download Converted File (before saving)
```
GET /api/download/:file_id?title=song-name
```

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
- `PORT` - Server port (set automatically by Railway)

## Deployment to Railway

1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Add PostgreSQL plugin in Railway
4. Set environment variables
5. Deploy

## Local Development

```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."
export SESSION_SECRET="your-secret"
python main.py
```

## React Frontend Integration

Example fetch call:
```javascript
const convertVideo = async (url) => {
  const response = await fetch('https://your-api.railway.app/api/convert', {
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
```
