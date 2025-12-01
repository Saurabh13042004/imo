#!/usr/bin/env python3
"""
Gemini AI Setup Guide
Quick reference for setting up Google Gemini API
"""

SETUP_GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║         Product Aggregator - Google Gemini AI Setup Guide                  ║
╚════════════════════════════════════════════════════════════════════════════╝

✨ WHAT'S NEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The system now uses Google Gemini AI instead of OpenAI for review analysis.
✅ Faster responses
✅ Free tier available (60 requests/minute)
✅ Better for product review analysis
✅ Simpler API integration

🔑 STEP 1: GET YOUR GEMINI API KEY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Open: https://makersuite.google.com/app/apikey
2. Click the "Create API Key" button
3. Select "Create API Key in new Google Cloud project" or existing project
4. Copy the API key (it starts with "AI...")
5. Keep it safe!

📝 STEP 2: CONFIGURE YOUR APPLICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Option A: Environment File (.env)
────────────────────────────────────
1. Open the .env file in your project
2. Find or add this line:
   GEMINI_API_KEY=your_api_key_here

3. Replace "your_api_key_here" with your actual key:
   GEMINI_API_KEY=AIzaSyDxZ5q...

Option B: Docker
────────────────────────────────────
1. Open docker-compose.yml
2. Add your key:
   environment:
     GEMINI_API_KEY: AIzaSyDxZ5q...

Option C: Command Line (temporary)
────────────────────────────────────
export GEMINI_API_KEY="AIzaSyDxZ5q..."

🚀 STEP 3: INSTALL DEPENDENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pip install -r requirements.txt

This will install:
- google-generativeai==0.3.1  ← New Gemini library

✅ STEP 4: VERIFY SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python -c "
import google.generativeai as genai
print('✅ Gemini library installed successfully')
"

🧪 STEP 5: TEST YOUR CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run this test script:

```python
import asyncio
import os
from app.services.ai_service import AIService

async def test_gemini():
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.initialized:
        print("❌ GEMINI_API_KEY not found!")
        return
    
    print("✅ AI Service initialized")
    
    # Test sentiment analysis
    test_review = "This product is amazing! Great quality and fast shipping."
    sentiment = await ai_service.analyze_sentiment(test_review)
    print(f"✅ Sentiment Analysis: {sentiment}")
    
    # Test pro/con extraction
    reviews = [
        "Great product, arrived on time",
        "Good quality but expensive",
        "Excellent customer service"
    ]
    pros_cons = await ai_service.extract_pros_cons(reviews)
    print(f"✅ Pros/Cons Extraction: {pros_cons}")
    
    print("\n✅ All tests passed!")

# Run the test
asyncio.run(test_gemini())
```

🎯 FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Review Summarization - Generate concise summaries
✅ Sentiment Analysis - Classify as positive/negative/neutral
✅ Pros/Cons Extraction - Identify key advantages and disadvantages
✅ Title Summarization - Create short product summaries

⚡ QUOTAS & LIMITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Free Tier:
├─ 60 requests per minute
├─ 1,000 requests per day
└─ No credit card required

Paid Tier:
├─ Higher quotas available
├─ 30 free requests per minute
└─ Pay-as-you-go pricing

📊 COMPARISON: OpenAI vs Gemini
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature              │ OpenAI GPT-3.5      │ Gemini Pro
────────────────────┼────────────────────┼──────────────────
Cost                │ $0.002 per request  │ Free (generous tier)
Speed               │ 2-3 seconds         │ 1-2 seconds
Review Analysis     │ Good                │ Excellent
Setup Complexity    │ Complex             │ Simple
API Simplicity      │ Medium              │ Simple
Context Window      │ 4,096               │ 32,000 tokens

🔗 USEFUL LINKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Get API Key:      https://makersuite.google.com/app/apikey
📍 Documentation:    https://ai.google.dev/tutorials
📍 API Reference:    https://ai.google.dev/api
📍 Python SDK:       https://github.com/google/generative-ai-python
📍 Community:        https://makersuite.google.com/waitlist

❓ TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue: "Gemini API key not configured"
Solution: Check GEMINI_API_KEY is in your .env file

Issue: "API quota exceeded"
Solution: Wait a minute or upgrade to paid tier

Issue: "Import error for google.generativeai"
Solution: Run: pip install google-generativeai

Issue: "Invalid API key"
Solution: Verify you copied the full key from makersuite.google.com

💡 TIPS & BEST PRACTICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Cache results to avoid repeated API calls
   └─ Already implemented in the system!

2. Use shorter reviews for faster processing
   └─ System limits to 10 reviews per summarization

3. Monitor your quota usage
   └─ Check at: https://makersuite.google.com/app/apikey

4. Keep your API key private
   └─ Never commit .env to version control

5. Batch your requests
   └─ Process reviews in batches for efficiency

🎓 EXAMPLE USAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In your application:

    from app.services import AIService
    
    # Initialize
    ai_service = AIService()
    
    # Analyze single review sentiment
    sentiment = await ai_service.analyze_sentiment("Great product!")
    
    # Summarize multiple reviews
    reviews = ["Good quality", "Fast shipping", "Excellent service"]
    summary = await ai_service.summarize_reviews(reviews, "Product Name")
    
    # Extract pros and cons
    analysis = await ai_service.extract_pros_cons(reviews)
    print(analysis["pros"])    # List of pros
    print(analysis["cons"])    # List of cons

🚀 READY TO GO!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your system is now configured with Google Gemini AI!

Next steps:
1. Start your application: uvicorn app.main:app --reload
2. Visit: http://localhost:8000/docs
3. Try the search and review analysis endpoints

For questions: Check GEMINI_MIGRATION.md for detailed documentation

═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(SETUP_GUIDE)
