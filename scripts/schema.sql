-- Song table schema for Neon PostgreSQL
-- Usage: psql "your-neon-connection-string" -f scripts/schema.sql

CREATE TABLE IF NOT EXISTS song (
    id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    artist VARCHAR(256) DEFAULT 'Unknown Artist',
    duration INTEGER DEFAULT 0,
    youtube_url VARCHAR(512),
    audio_data BYTEA NOT NULL,
    file_size INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_song_created_at ON song(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_song_artist ON song(artist);
CREATE INDEX IF NOT EXISTS idx_song_youtube_url ON song(youtube_url);

-- Grant permissions (if using a specific user)
-- Uncomment and modify if needed:
-- GRANT ALL PRIVILEGES ON song TO your_user;
-- GRANT USAGE, SELECT ON SEQUENCE song_id_seq TO your_user;
