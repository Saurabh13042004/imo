#!/usr/bin/env python3
"""
Getting Started Checklist for Product Aggregator & Review System
Run this to verify all components are in place
"""

import os
import sys
from pathlib import Path

def check_file_exists(path: str, name: str) -> bool:
    """Check if a file exists."""
    exists = os.path.isfile(path)
    status = "✅" if exists else "❌"
    print(f"{status} {name}")
    return exists

def check_dir_exists(path: str, name: str) -> bool:
    """Check if a directory exists."""
    exists = os.path.isdir(path)
    status = "✅" if exists else "❌"
    print(f"{status} {name}")
    return exists

def main():
    print("\n" + "="*60)
    print("Product Aggregator & Review System - Setup Checklist")
    print("="*60 + "\n")

    base_path = os.path.dirname(os.path.abspath(__file__))
    all_ok = True

    # Check configuration files
    print("📋 Configuration Files:")
    all_ok &= check_file_exists(os.path.join(base_path, ".env.example"), ".env.example")
    all_ok &= check_file_exists(os.path.join(base_path, "requirements.txt"), "requirements.txt")
    all_ok &= check_file_exists(os.path.join(base_path, ".gitignore"), ".gitignore")

    # Check Docker files
    print("\n🐳 Docker Files:")
    all_ok &= check_file_exists(os.path.join(base_path, "docker-compose.yml"), "docker-compose.yml")
    all_ok &= check_file_exists(os.path.join(base_path, "Dockerfile"), "Dockerfile")

    # Check documentation
    print("\n📚 Documentation:")
    all_ok &= check_file_exists(os.path.join(base_path, "README.md"), "README.md")
    all_ok &= check_file_exists(os.path.join(base_path, "QUICKSTART.md"), "QUICKSTART.md")
    all_ok &= check_file_exists(os.path.join(base_path, "IMPLEMENTATION_GUIDE.md"), "IMPLEMENTATION_GUIDE.md")
    all_ok &= check_file_exists(os.path.join(base_path, "DELIVERY_SUMMARY.md"), "DELIVERY_SUMMARY.md")
    all_ok &= check_file_exists(os.path.join(base_path, "FILE_MANIFEST.md"), "FILE_MANIFEST.md")

    # Check app directories
    print("\n📁 App Directories:")
    all_ok &= check_dir_exists(os.path.join(base_path, "app"), "app/")
    all_ok &= check_dir_exists(os.path.join(base_path, "app/models"), "app/models/")
    all_ok &= check_dir_exists(os.path.join(base_path, "app/schemas"), "app/schemas/")
    all_ok &= check_dir_exists(os.path.join(base_path, "app/api"), "app/api/")
    all_ok &= check_dir_exists(os.path.join(base_path, "app/api/routes"), "app/api/routes/")
    all_ok &= check_dir_exists(os.path.join(base_path, "app/services"), "app/services/")
    all_ok &= check_dir_exists(os.path.join(base_path, "app/integrations"), "app/integrations/")
    all_ok &= check_dir_exists(os.path.join(base_path, "app/utils"), "app/utils/")

    # Check app files
    print("\n🔧 App Core Files:")
    all_ok &= check_file_exists(os.path.join(base_path, "app/__init__.py"), "app/__init__.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/main.py"), "app/main.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/config.py"), "app/config.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/database.py"), "app/database.py")

    # Check models
    print("\n📊 Database Models:")
    all_ok &= check_file_exists(os.path.join(base_path, "app/models/__init__.py"), "app/models/__init__.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/models/product.py"), "app/models/product.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/models/review.py"), "app/models/review.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/models/video.py"), "app/models/video.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/models/search_cache.py"), "app/models/search_cache.py")

    # Check schemas
    print("\n📋 API Schemas:")
    all_ok &= check_file_exists(os.path.join(base_path, "app/schemas/__init__.py"), "app/schemas/__init__.py")

    # Check API routes
    print("\n🛣️ API Routes:")
    all_ok &= check_file_exists(os.path.join(base_path, "app/api/__init__.py"), "app/api/__init__.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/api/dependencies.py"), "app/api/dependencies.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/api/routes/search.py"), "app/api/routes/search.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/api/routes/products.py"), "app/api/routes/products.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/api/routes/reviews.py"), "app/api/routes/reviews.py")

    # Check services
    print("\n⚙️ Services:")
    all_ok &= check_file_exists(os.path.join(base_path, "app/services/__init__.py"), "app/services/__init__.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/services/search_service.py"), "app/services/search_service.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/services/review_service.py"), "app/services/review_service.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/services/video_service.py"), "app/services/video_service.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/services/ai_service.py"), "app/services/ai_service.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/services/cache_service.py"), "app/services/cache_service.py")

    # Check integrations
    print("\n🔌 Integrations:")
    all_ok &= check_file_exists(os.path.join(base_path, "app/integrations/__init__.py"), "app/integrations/__init__.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/integrations/amazon.py"), "app/integrations/amazon.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/integrations/walmart.py"), "app/integrations/walmart.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/integrations/google_shopping.py"), "app/integrations/google_shopping.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/integrations/youtube.py"), "app/integrations/youtube.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/integrations/reddit.py"), "app/integrations/reddit.py")

    # Check utils
    print("\n🛠️ Utilities:")
    all_ok &= check_file_exists(os.path.join(base_path, "app/utils/__init__.py"), "app/utils/__init__.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/utils/helpers.py"), "app/utils/helpers.py")
    all_ok &= check_file_exists(os.path.join(base_path, "app/utils/validators.py"), "app/utils/validators.py")

    # Check alembic
    print("\n📦 Alembic Database Migrations:")
    all_ok &= check_dir_exists(os.path.join(base_path, "alembic"), "alembic/")
    all_ok &= check_file_exists(os.path.join(base_path, "alembic/env.py"), "alembic/env.py")
    all_ok &= check_file_exists(os.path.join(base_path, "alembic/alembic.ini"), "alembic/alembic.ini")
    all_ok &= check_file_exists(os.path.join(base_path, "alembic/versions/001_initial.py"), "alembic/versions/001_initial.py")

    # Check tests
    print("\n🧪 Tests:")
    all_ok &= check_dir_exists(os.path.join(base_path, "tests"), "tests/")

    # Print summary
    print("\n" + "="*60)
    if all_ok:
        print("✅ All files and directories are in place!")
        print("\n📝 Next Steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to .env:")
        print("   - RAPIDAPI_KEY")
        print("   - OPENAI_API_KEY")
        print("   - YOUTUBE_API_KEY")
        print("   - REDDIT_CLIENT_ID & REDDIT_CLIENT_SECRET")
        print("3. Set up PostgreSQL database")
        print("4. Install dependencies: pip install -r requirements.txt")
        print("5. Run migrations: alembic upgrade head")
        print("6. Start server: uvicorn app.main:app --reload")
        print("\n📖 Documentation:")
        print("- Quick Start: See QUICKSTART.md")
        print("- Full Guide: See IMPLEMENTATION_GUIDE.md")
        print("- API Docs: http://localhost:8000/docs (after starting server)")
        return 0
    else:
        print("❌ Some files or directories are missing!")
        print("Please check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
