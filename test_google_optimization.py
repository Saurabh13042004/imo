"""Test optimized Google scraper performance."""

import sys
import time
import asyncio
sys.path.insert(0, 'backend')

from app.services.google_review_service import GoogleReviewService

async def test_google_scraper():
    """Test optimized scraper on a product."""
    
    # Example Google Shopping URL
    google_url = "https://www.google.com/shopping/product/1234567890"
    
    service = GoogleReviewService()
    
    print("=" * 60)
    print("TESTING OPTIMIZED GOOGLE REVIEW SCRAPER")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Test with asyncio.to_thread (like in the API)
        result = await asyncio.to_thread(
            service.fetch_google_reviews,
            google_shopping_url=google_url,
            product_name="Test Product"
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n✓ Scraping completed in {elapsed:.1f} seconds")
        print(f"  Reviews extracted: {len(result)}")
        if result:
            print(f"  Sample review: {result[0]['text'][:100]}...")
        
        # Performance assessment
        if elapsed < 8:
            print("  🚀 EXCELLENT - Fast parallel execution!")
        elif elapsed < 12:
            print("  ✓ GOOD - Notable improvement from parallel processing")
        else:
            print("  ⚠ Could be faster - may need additional optimization")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nStarting optimized scraper test...")
    asyncio.run(test_google_scraper())
