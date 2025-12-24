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

# Set the sqlalchemy.url from environment
from app.config import settings
cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Run upgrade
print(f"Applying migrations to: {settings.DATABASE_URL}")
command.upgrade(cfg, "head")
print("✅ Migrations applied successfully!")
