# SerpAPI Geo-Targeting - Architecture & Flow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SharedSearchInput.tsx                                       │  │
│  │  ├─ Query input                                             │  │
│  │  ├─ Country selector (dropdown)  ← India, US, etc.         │  │
│  │  ├─ City input (optional)         ← Bengaluru              │  │
│  │  └─ Language selector             ← Hindi, English, etc.   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ useProductSearch() Hook                                    │  │
│  │  └─ Sends: {keyword, country, city, language}             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                             ↓ HTTP POST /api/v1/search
                      
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ POST /api/v1/search (routes/search.py)                     │  │
│  │  └─ Validate SearchRequest                                │  │
│  │     {keyword, country, city, language, zipcode}          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SearchService.search_all_sources()                         │  │
│  │  ├─ Extract: country, city, language                      │  │
│  │  ├─ Build location: f"{city},{country}"                  │  │
│  │  └─ Call _search_google_shopping(                         │  │
│  │       keyword, location, country, language)              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ utils/geo.py - get_country_config()                        │  │
│  │  ├─ Input:  country = "India"                             │  │
│  │  └─ Output: {"gl": "in", "google_domain": "google.co.in"} │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ GoogleShoppingClient.search()                              │  │
│  │  ├─ Build params:                                         │  │
│  │  │  ├─ engine: "google_shopping"                          │  │
│  │  │  ├─ q: keyword                                         │  │
│  │  │  ├─ location: "Bengaluru,India"                        │  │
│  │  │  ├─ gl: "in"                                           │  │
│  │  │  ├─ hl: "hi"                                           │  │
│  │  │  └─ google_domain: "google.co.in"                      │  │
│  │  └─ Log params (comprehensive)                            │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                             ↓ HTTP GET
                      
┌─────────────────────────────────────────────────────────────────────┐
│                       SerpAPI (External)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  https://serpapi.com/search?                                       │
│    engine=google_shopping&                                         │
│    q=samsung+tv&                                                   │
│    location=Bengaluru,India&                                       │
│    gl=in&                                                          │
│    hl=hi&                                                          │
│    google_domain=google.co.in&                                     │
│    api_key=YOUR_KEY                                                │
│                                                                    │
│  Returns:                                                          │
│  {                                                                 │
│    "shopping_results": [                                           │
│      {"title": "Samsung 43\" TV", "price": "₹25,999", ...},       │
│      {"title": "Samsung 55\" QLED TV", "price": "₹52,999", ...},  │
│      ...                                                           │
│    ]                                                               │
│  }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                             ↑
                             │ JSON Response
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│                      BACKEND (continued)                            │
├────────────────────────────┼────────────────────────────────────────┤
│                            │                                        │
│  ┌─────────────────────────┘─────────────────────────────────────┐ │
│  │ SearchService._convert_to_product_responses()                │ │
│  │  ├─ Transform SerpAPI response                              │ │
│  │  ├─ Parse prices, ratings, etc.                            │ │
│  │  └─ Return List[ProductResponse]                           │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                            ↓                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Return SearchResponse                                       │  │
│  │  {                                                          │  │
│  │    "success": true,                                         │  │
│  │    "keyword": "samsung tv",                                 │  │
│  │    "country": "India",                                      │  │
│  │    "city": "Bengaluru",                                     │  │
│  │    "language": "hi",                                        │  │
│  │    "total_results": 48,                                     │  │
│  │    "results": [...]                                         │  │
│  │  }                                                          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                             ↓ HTTP 200 + JSON
                      
┌────────────────────────────┬────────────────────────────────────────┐
│                      FRONTEND (React)                              │
├────────────────────────────┬────────────────────────────────────────┤
│                            ↓                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ useProductSearch() - State Update                          │  │
│  │  └─ setProducts(response.results)                          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Search.tsx - Render Results                                │  │
│  │  └─ Display: "Found 48 products in India - Bengaluru"     │  │
│  │      └─ ProductGrid with Indian retailers & prices        │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Search Request

```
Frontend Form Input
│
├─ query: "samsung tv"
├─ country: "India"           ← Selected by user
├─ city: "Bengaluru"          ← Entered by user (optional)
├─ language: "hi"             ← Selected by user
└─ zipcode: "500001"          ← Auto-detected or provided (NOT USED)
│
↓ JSON Payload
│
POST /api/v1/search
{
  "keyword": "samsung tv",
  "country": "India",
  "city": "Bengaluru",
  "language": "hi",
  "zipcode": "500001"
}
│
↓ Backend Processing
│
SearchService.search_all_sources()
│
├─ Extract: country="India", city="Bengaluru", language="hi"
├─ Build location: "Bengaluru,India"
├─ Call get_country_config("India")
│  └─ Returns: {"gl": "in", "google_domain": "google.co.in"}
│
└─ Call GoogleShoppingClient.search(
     query="samsung tv",
     location="Bengaluru,India",
     country="India",
     language="hi"
   )
│
↓ SerpAPI Call Built
│
url = "https://serpapi.com/search"
params = {
  "engine": "google_shopping",
  "q": "samsung tv",
  "location": "Bengaluru,India",
  "gl": "in",                          ← Google locale for India
  "hl": "hi",                          ← Hindi interface
  "google_domain": "google.co.in",     ← Indian domain
  "api_key": "YOUR_KEY"
}
│
↓ SerpAPI Request
│
GET https://serpapi.com/search?
  engine=google_shopping&
  q=samsung+tv&
  location=Bengaluru,India&
  gl=in&
  hl=hi&
  google_domain=google.co.in&
  api_key=...
│
↓ SerpAPI Response
│
{
  "shopping_results": [
    {
      "position": 1,
      "title": "Samsung 43\" Full HD Smart TV",
      "price": "₹25,999",
      "source": "Flipkart",
      "link": "...",
      "image": "..."
    },
    ...
  ]
}
│
↓ Frontend Display
│
Results shown with Indian retailers & INR pricing:
- Flipkart: ₹25,999
- Amazon.in: ₹27,999
- Reliance Digital: ₹26,499
- etc.
```

---

## Country Configuration Flow

```
User selects country: "India"
         ↓
SearchService receives "India"
         ↓
get_country_config("India")
         ↓
Lookup in COUNTRY_CONFIG dict:
{
  "India": {
    "gl": "in",
    "google_domain": "google.co.in"
  },
  ...
}
         ↓
Returns: {"gl": "in", "google_domain": "google.co.in"}
         ↓
Build SerpAPI params:
{
  "gl": "in"                      ← Google locale
  "google_domain": "google.co.in" ← Domain
}
         ↓
SerpAPI returns India-specific results
```

---

## Backward Compatibility

```
Old Frontend (No Changes)
  │
  ├─ Sends only: {keyword, zipcode}
  │
  ↓
  
New Backend (Backward Compatible)
  │
  ├─ Defaults applied:
  │  ├─ country: "United States"
  │  ├─ city: ""
  │  └─ language: "en"
  │
  ├─ IGNORES zipcode (legacy field)
  │
  └─ Proceeds with defaults
     (Works, but gives US results)
  
New Frontend (Recommended)
  │
  ├─ Sends: {keyword, country, city, language}
  │
  └─ Gets geo-targeted results ✅
```

---

## Country Mapping Reference

```
Input Country        → GL Code → Google Domain
─────────────────────────────────────────────
"India"              → "in"   → "google.co.in"
"United States"      → "us"   → "google.com"
"Canada"             → "ca"   → "google.ca"
"United Kingdom"     → "uk"   → "google.co.uk"
"Brazil"             → "br"   → "google.com.br"
"Mexico"             → "mx"   → "google.com.mx"
"Germany"            → "de"   → "google.de"
"France"             → "fr"   → "google.fr"
"Japan"              → "jp"   → "google.co.jp"
"Australia"          → "au"   → "google.com.au"
(Unknown)            → "us"   → "google.com" (default)
```

---

## Error Handling

```
Search Request
    ↓
ValidateSearchQuery()
    ├─ If invalid: Return 400 Bad Request
    └─ If valid: Continue
    ↓
search_all_sources()
    ├─ GoogleShoppingClient not init?
    │   └─ Return 500 error
    └─ Client initialized: Continue
    ↓
SerpAPI Call
    ├─ Network error?
    │   └─ Log error, return empty results
    ├─ API error?
    │   └─ Log error, return empty results
    └─ Success: Return results
    ↓
Transform Results
    ├─ Invalid data?
    │   └─ Skip that result
    └─ Valid: Add to results
    ↓
Return SearchResponse
    ├─ Success: 200 with results
    └─ Error: 500 with error message
```

---

## Logging Hierarchy

```
LEVEL       COMPONENT              MESSAGE
──────      ─────────────────────  ─────────────────────────────
INFO        SearchService          [SearchService] Starting search:
            (start)                  Keyword: samsung tv
                                     Country: India
                                     City: Bengaluru
                                     Location for SerpAPI: Bengaluru,India
            
            │ ↓

INFO        geo.py                 [GeoConfig] Country: India 
            (lookup)               → gl=in, domain=google.co.in
            
            │ ↓

INFO        GoogleShoppingClient   [SerpAPI Request] Final parameters:
            (request build)          engine: google_shopping
                                     q: samsung tv
                                     location: Bengaluru,India
                                     gl: in
                                     hl: hi
                                     google_domain: google.co.in
            
            │ ↓

INFO        GoogleShoppingClient   [SerpAPI Response] Status: Success
            (response parse)         Results: 48
                                     Query: samsung tv
                                     Location: Bengaluru,India
                                     Country: India
            
            │ ↓

INFO        SearchService          [SearchService] Search completed
            (finish)               in 1.23s: Found 48 unique products

DEBUG       (if enabled)           Individual product transformations
            
ERROR       (if any)               Error details with stack trace
```

---

## Component Dependencies

```
Routes
└── search.py
    └── SearchService
        ├── GoogleShoppingClient
        │   ├── geo.py (get_country_config)
        │   └── log_serpapi_params
        └── schemas
            ├── SearchRequest
            └── SearchResponse

Services
├── search_service.py
│   ├── integrations.google_shopping
│   ├── utils.geo
│   └── schemas
│
└── product_service.py
    ├── integrations.google_shopping
    ├── utils.geo
    └── schemas

Utilities
└── geo.py (standalone, reusable)
    ├── COUNTRY_CONFIG (data)
    ├── get_country_config()
    ├── build_serpapi_location()
    └── log_serpapi_params()
```

---

## Testing Scenarios

```
Scenario 1: India Search (Happy Path)
─────────────────────────────────────
Input:  keyword="samsung tv", country="India", city="Bengaluru", language="hi"
Output: Indian retailers (Flipkart, Amazon.in, etc.) with INR prices
Logs:   Confirm gl=in, google_domain=google.co.in

Scenario 2: US Search
──────────────────
Input:  keyword="iphone 15", country="United States", city="Austin", language="en"
Output: US retailers (Best Buy, Amazon.com, Walmart) with USD prices
Logs:   Confirm gl=us, google_domain=google.com

Scenario 3: Backward Compatibility
──────────────────────────────────
Input:  keyword="product", zipcode="12345" (OLD format)
Output: Works with defaults (US, English)
Logs:   Shows defaults applied

Scenario 4: URL Persistence
───────────────────────────
Action: Search, navigate, come back
Result: URL preserves country, city, language
URL:    /search?q=samsung+tv&country=India&city=Bengaluru&language=hi

Scenario 5: Missing Optional Fields
──────────────────────────────────
Input:  keyword="tv" (country defaults, city empty)
Result: Uses "Country" as location string (no city)
SerpAPI: location="India" (not "City,India")
```

---

**Created**: December 18, 2025  
**Status**: ✅ Complete & Production Ready  
**Next**: Frontend Implementation (see SERPAPI_FRONTEND_GUIDE.ts)
