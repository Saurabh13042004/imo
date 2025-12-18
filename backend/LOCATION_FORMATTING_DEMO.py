"""
Demo of SerpAPI location formatting and logging.

This demonstrates:
1. How location formatting works (zipcode → "City, State, Country")
2. How location is passed to SerpAPI
3. The comprehensive logging that tracks all API calls
"""

import asyncio
from app.services.location_service import LocationService
from app.utils.helpers import format_location_for_serpapi


async def demo_location_formatting():
    """Demo location formatting for various zipcodes."""
    
    test_cases = [
        ("60607", "Chicago, Illinois"),  # Chicago
        ("10001", "New York, New York"),  # New York
        ("90210", "Los Angeles, California"),  # LA
        ("50000", "Hyderabad, Telangana"),  # Hyderabad, India
        ("40001", "Mumbai, Maharashtra"),  # Mumbai, India
        ("11001", "New Delhi, Delhi"),  # New Delhi, India
    ]
    
    print("\n" + "="*80)
    print("LOCATION FORMATTING DEMO")
    print("="*80 + "\n")
    
    for zipcode, expected in test_cases:
        formatted = await LocationService.get_location_string_for_serpapi(zipcode)
        print(f"Zipcode: {zipcode:6} → Formatted for SerpAPI: {formatted}")
        print(f"  (Expected contains: {expected})\n")


def demo_serpapi_request_format():
    """Demo how SerpAPI request will look with location parameter."""
    
    print("\n" + "="*80)
    print("SERPAPI REQUEST FORMAT DEMO")
    print("="*80 + "\n")
    
    examples = [
        {
            "location": "Austin, Texas, United States",
            "query": "iPhone 15",
            "description": "US Location"
        },
        {
            "location": "Hyderabad, Telangana, India",
            "query": "iPhone 15",
            "description": "India Location"
        },
        {
            "location": "Toronto, Ontario, Canada",
            "query": "iPhone 15",
            "description": "Canada Location"
        },
    ]
    
    print("Expected SerpAPI calls with location parameter:\n")
    
    for example in examples:
        print(f"\n{example['description']}:")
        print("  curl --get https://serpapi.com/search \\")
        print(f"    -d engine=\"google_shopping\" \\")
        print(f"    -d q=\"{example['query']}\" \\")
        print(f"    -d location=\"{example['location']}\" \\")
        print(f"    -d api_key=\"YOUR_API_KEY\"")


def show_logging_output():
    """Show what logging output will look like."""
    
    print("\n" + "="*80)
    print("EXPECTED LOGGING OUTPUT")
    print("="*80 + "\n")
    
    log_examples = [
        "[SearchService] Calling Google Shopping:\n  Keyword: iPhone 15\n  Location: Austin, Texas, United States\n  Will call SerpAPI with: engine=google_shopping, q=iPhone 15, location=Austin, Texas, United States",
        "[SerpAPI] Making Google Shopping request:\n  URL: https://serpapi.com/search\n  Query: iPhone 15\n  Location: Austin, Texas, United States\n  Engine: google_shopping (via tbm=shop)\n  Request params (sanitized): {\"q\": \"iPhone 15\", \"tbm\": \"shop\", \"num\": 100, \"location\": \"Austin, Texas, United States\"}",
        "[SerpAPI] Response received:\n  Status: Success\n  Results count: 48\n  Search params used: engine=google_shopping, q=iPhone 15, location=Austin, Texas, United States",
        "[Location] Resolved zipcode 60607 to Chicago, Illinois, United States",
    ]
    
    for i, log in enumerate(log_examples, 1):
        print(f"Log Message {i}:")
        print(f"  {log}\n")


if __name__ == "__main__":
    print("\n\n")
    print("█" * 80)
    print("█ " + " " * 76 + " █")
    print("█ " + "SerpAPI Location Formatting & Logging Demo".center(76) + " █")
    print("█ " + " " * 76 + " █")
    print("█" * 80)
    
    # Show formatting demo
    demo_serpapi_request_format()
    
    # Show logging output
    show_logging_output()
    
    # Show async location formatting
    print("\n\n" + "="*80)
    print("RUNNING ACTUAL LOCATION FORMATTING")
    print("="*80 + "\n")
    
    asyncio.run(demo_location_formatting())
    
    print("\n" + "█" * 80)
    print("█ " + "Summary".center(76) + " █")
    print("█" * 80 + "\n")
    
    print("Changes Made:")
    print("  1. LocationService converts zipcode to 'City, State, Country' format")
    print("  2. SearchService uses LocationService to format location before passing to SerpAPI")
    print("  3. GoogleShoppingClient logs the exact SerpAPI request with location parameter")
    print("  4. ProductService also formats location when fetching enrichment data")
    print("\nResult:")
    print("  ✓ SerpAPI receives properly formatted location: 'Austin, Texas, United States'")
    print("  ✓ All API calls are logged comprehensively")
    print("  ✓ Easy to debug location-related issues\n")
