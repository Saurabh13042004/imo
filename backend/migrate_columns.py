#!/usr/bin/env python
"""Directly apply SQL migrations to add missing columns."""

import asyncio
import asyncpg
from app.config import settings
import sys

async def run_migration():
    # Parse database URL - remove asyncpg from the URL for asyncpg.connect
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Connecting to: {db_url}")
    
    try:
        conn = await asyncpg.connect(db_url)
        
        # Check if status column exists
        try:
            await conn.execute("SELECT status FROM user_reviews LIMIT 1")
            print("✅ Column 'status' already exists")
        except asyncpg.exceptions.UndefinedColumnError:
            print("❌ Column 'status' missing - adding it...")
            await conn.execute("""
                ALTER TABLE user_reviews 
                ADD COLUMN status VARCHAR DEFAULT 'pending' NOT NULL
            """)
            print("✅ Added 'status' column")
        
        # Check if s3_key column exists
        try:
            await conn.execute("SELECT s3_key FROM user_reviews LIMIT 1")
            print("✅ Column 's3_key' already exists")
        except asyncpg.exceptions.UndefinedColumnError:
            print("❌ Column 's3_key' missing - adding it...")
            await conn.execute("""
                ALTER TABLE user_reviews 
                ADD COLUMN s3_key VARCHAR
            """)
            print("✅ Added 's3_key' column")
        
        # Check if updated_at column exists
        try:
            await conn.execute("SELECT updated_at FROM user_reviews LIMIT 1")
            print("✅ Column 'updated_at' already exists")
        except asyncpg.exceptions.UndefinedColumnError:
            print("❌ Column 'updated_at' missing - adding it...")
            await conn.execute("""
                ALTER TABLE user_reviews 
                ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            """)
            print("✅ Added 'updated_at' column")
        
        # Create indexes
        try:
            await conn.execute("CREATE INDEX idx_user_reviews_status ON user_reviews(status)")
            print("✅ Created index on 'status'")
        except asyncpg.exceptions.DuplicateObjectError:
            print("✅ Index on 'status' already exists")
        
        try:
            await conn.execute("CREATE INDEX idx_user_reviews_product_status ON user_reviews(product_id, status)")
            print("✅ Created index on 'product_id, status'")
        except asyncpg.exceptions.DuplicateObjectError:
            print("✅ Index on 'product_id, status' already exists")
        
        await conn.close()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_migration())
