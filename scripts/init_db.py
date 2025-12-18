#!/usr/bin/env python3
"""
Initialize Neon PostgreSQL database with song table.
Usage:
    export DATABASE_URL="postgresql://user:password@...?sslmode=require"
    python scripts/init_db.py
"""

import os
import sys
import psycopg2

def init_database():
    """Create database schema."""
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not set")
        print("Example:")
        print("  export DATABASE_URL='postgresql://user:pass@ep-xxxx.us-east-1.neon.tech/dbname?sslmode=require'")
        return False
    
    schema_sql = """
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
    
    CREATE INDEX IF NOT EXISTS idx_song_created_at ON song(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_song_artist ON song(artist);
    CREATE INDEX IF NOT EXISTS idx_song_youtube_url ON song(youtube_url);
    """
    
    try:
        print("🔄 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📝 Creating schema...")
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✓ Song table created")
        print("✓ Indexes created")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database initialization complete!")
        return True
        
    except psycopg2.errors.DuplicateTable:
        print("⚠ Tables already exist (this is fine)")
        return True
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if "sslmode" in str(e).lower():
            print("   Make sure your URL includes: ?sslmode=require")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
