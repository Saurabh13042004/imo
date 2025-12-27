#!/usr/bin/env python
"""Apply migrations using alembic command."""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Change to alembic directory
os.chdir(Path(__file__).parent / "alembic")

# Import alembic CLI
from alembic.config import Config
from alembic import command

# Create config
cfg = Config("alembic.ini")

# Set the sqlalchemy.url from environment, but convert async to sync for migrations
from app.config import settings
database_url = settings.DATABASE_URL

# Convert async postgresql+asyncpg:// to sync postgresql:// for Alembic
if "postgresql+asyncpg://" in database_url:
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

cfg.set_main_option("sqlalchemy.url", database_url)

# Run upgrade
print(f"Applying migrations to: {database_url}")
command.upgrade(cfg, "head")
print("✅ Migrations applied successfully!")
