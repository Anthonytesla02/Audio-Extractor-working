#!/usr/bin/env python3
"""
Test connection to Neon.tech PostgreSQL database.
Verifies database configuration and schema.
Usage:
    export DATABASE_URL="postgresql://user:password@...?sslmode=require"
    python scripts/test_connection.py
"""

import os
import sys
import psycopg2

def test_connection():
    """Test database connection and schema."""
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Please set your Neon connection string:")
        print("  export DATABASE_URL='postgresql://user:password@...?sslmode=require'")
        return False
    
    try:
        print("🔄 Testing database connection...\n")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test 1: Connection
        cursor.execute("SELECT 1")
        cursor.fetchone()
        print("✓ Database connection successful")
        
        # Test 2: Schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'song'
        """)
        result = cursor.fetchone()
        
        if not result:
            print("⚠ Song table not found")
            print("  Run: python scripts/init_db.py")
            cursor.close()
            conn.close()
            return False
        
        print("✓ Song table exists")
        
        # Test 3: Columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'song'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"✓ Found {len(columns)} columns:")
        for col, dtype in columns:
            print(f"  - {col}: {dtype}")
        
        # Test 4: Indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'song' AND schemaname = 'public'
        """)
        indexes = cursor.fetchall()
        print(f"✓ Found {len(indexes)} indexes")
        
        # Test 5: Insert & retrieve
        cursor.execute("""
            INSERT INTO song (title, artist, duration, youtube_url, audio_data, file_size)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            "Test Song",
            "Test Artist",
            180,
            "https://youtube.com/watch?v=test",
            b"test_data",
            9
        ))
        test_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✓ Insert test successful (ID: {test_id})")
        
        # Test 6: Query
        cursor.execute("SELECT COUNT(*) FROM song WHERE title = %s", ("Test Song",))
        count = cursor.fetchone()[0]
        print(f"✓ Query successful ({count} record found)")
        
        # Cleanup
        cursor.execute("DELETE FROM song WHERE id = %s", (test_id,))
        conn.commit()
        print("✓ Cleanup complete")
        
        cursor.close()
        conn.close()
        
        print("\n✅ All checks passed! Database is ready.")
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
    success = test_connection()
    sys.exit(0 if success else 1)
