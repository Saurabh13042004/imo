#!/usr/bin/env python3
"""Quick test of Selenium Google Reviews scraper."""

import logging
from app.services.google_review_service import GoogleReviewService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test URL (iPhone 17)
url = "https://www.google.co.in/search?ibp=oshop&q=iphone%2017&prds=catalogid:14658515877207651442,headlineOfferDocid:5165600615243989691,imageDocid:12454427096991879944,rds:PC_6027158597472037202|PROD_PC_6027158597472037202,gpcid:6027158597472037202,mid:576462866558881327,pvt:hg&hl=en&gl=in&udm=28"

# Test
service = GoogleReviewService()
result = service.fetch_google_reviews(
    google_shopping_url=url,
    product_name="Apple iPhone 17",
    max_clicks=5
)

print("\n" + "="*80)
print("RESULT:")
print("="*80)
print(f"Success: {result['success']}")
print(f"Total Reviews: {result.get('total_reviews', 0)}")
if result['reviews']:
    print(f"Sample reviews:")
    for i, review in enumerate(result['reviews'][:3], 1):
        print(f"  {i}. {review.get('reviewer_name')} ({review.get('rating')}⭐)")
        print(f"     {review.get('title')}")
        print(f"     {review.get('text')[:100]}...")
else:
    print(f"Error: {result.get('error')}")
print("="*80)
