"""Product identity extraction and relevance scoring."""

import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def extract_product_identity(product_title: str) -> Dict[str, Any]:
    """
    Extract structured product identity from product title.
    
    Example:
    Input: "PlayStation PS5 Console - Fortnite Cobalt Star Disc Edition"
    Output: {
        "brand": "PlayStation",
        "model": "PS5",
        "edition": "Fortnite Cobalt Star",
        "category": "console",
        "keywords": ["ps5", "fortnite", "cobalt", "star", "console"]
    }
    """
    if not product_title or not isinstance(product_title, str):
        return {
            "brand": "",
            "model": "",
            "edition": "",
            "category": "",
            "keywords": []
        }

    title = product_title.strip()
    
    # Brand detection
    brand = ""
    brand_patterns = {
        "Sony": r"\bSony\b",
        "PlayStation": r"\bPlayStation\b|\bPS\b",
        "Microsoft": r"\bMicrosoft\b",
        "Xbox": r"\bXbox\b",
        "Nintendo": r"\bNintendo\b",
        "Apple": r"\bApple\b",
        "Samsung": r"\bSamsung\b",
        "LG": r"\bLG\b",
        "Dell": r"\bDell\b",
        "HP": r"\bHP\b",
        "Lenovo": r"\bLenovo\b",
        "ASUS": r"\bASUS\b",
        "Corsair": r"\bCorsair\b",
        "Razer": r"\bRazer\b",
        "SteelSeries": r"\bSteelSeries\b",
    }
    
    for brand_name, pattern in brand_patterns.items():
        if re.search(pattern, title, re.IGNORECASE):
            brand = brand_name
            break
    
    # Model detection (first number sequence or capitalized words after brand)
    model = ""
    model_patterns = [
        r"\b(PS5|PS4|PS3|XSX|Xbox Series X|Xbox One|Switch|iPad|iPhone)\b",
        r"\b([A-Z]+\d+[A-Z]*)\b",  # Patterns like PS5, RTX3090, etc.
    ]
    
    for pattern in model_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            model = match.group(1)
            break
    
    # Edition/variant detection (usually after dash or "Edition")
    edition = ""
    edition_match = re.search(r'[-–]\s*(.+?)(?:\s+Edition|\s+Disc|\s+Digital|\s+Pro|$)', title, re.IGNORECASE)
    if edition_match:
        edition = edition_match.group(1).strip()
    
    # Category detection
    category = ""
    category_keywords = {
        "console": r"\b(console|gaming console)\b",
        "headphones": r"\b(headphones|earbuds|wireless headphones)\b",
        "monitor": r"\b(monitor|display|screen)\b",
        "keyboard": r"\b(keyboard|mechanical keyboard)\b",
        "mouse": r"\b(mouse|gaming mouse)\b",
        "controller": r"\b(controller|gamepad)\b",
        "laptop": r"\b(laptop|notebook)\b",
        "phone": r"\b(phone|smartphone|iphone)\b",
        "tablet": r"\b(tablet|ipad)\b",
        "tv": r"\b(tv|television|4k tv)\b",
        "camera": r"\b(camera|dslr|mirrorless)\b",
    }
    
    for cat, pattern in category_keywords.items():
        if re.search(pattern, title, re.IGNORECASE):
            category = cat
            break
    
    # Extract all keywords (lowercased for matching)
    keywords = []
    # Add brand and model
    if brand:
        keywords.extend(brand.lower().split())
    if model:
        keywords.extend(model.lower().split())
    if edition:
        # Split edition into words and add significant ones
        for word in edition.split():
            if len(word) > 2 and word.lower() not in ["and", "the", "or", "of"]:
                keywords.append(word.lower())
    
    # Remove duplicates while preserving order
    keywords = list(dict.fromkeys(keywords))
    
    logger.debug(f"Extracted identity from '{product_title}': brand={brand}, model={model}, edition={edition}, category={category}")
    
    return {
        "brand": brand,
        "model": model,
        "edition": edition,
        "category": category,
        "keywords": keywords,
        "original_title": title
    }


def calculate_relevance_score(text: str, product_identity: Dict[str, Any]) -> float:
    """
    Calculate relevance score for a review text against product identity.
    
    Scoring:
    - +0.4 if model appears
    - +0.4 if edition appears (or major keywords)
    - +0.2 if ownership keywords appear
    
    Returns: float between 0.0 and 1.0
    """
    if not text or not isinstance(text, str):
        return 0.0
    
    text_lower = text.lower()
    score = 0.0
    
    # Check for model keyword (0.4 points)
    model = product_identity.get("model", "").lower()
    if model and model in text_lower:
        score += 0.4
        logger.debug(f"Model '{model}' found in text (+0.4)")
    
    # Check for edition/other keywords (0.4 points)
    keywords = product_identity.get("keywords", [])
    keywords_found = sum(1 for kw in keywords if kw and kw in text_lower)
    if keywords_found >= 1:
        score += min(0.4, 0.2 * keywords_found)  # Cap at 0.4
        logger.debug(f"Found {keywords_found} keywords in text (+{min(0.4, 0.2 * keywords_found)})")
    
    # Check for ownership/experience keywords (0.2 points)
    ownership_keywords = [
        "i own", "i bought", "i purchased", "i have",
        "i've been using", "i've owned", "been using",
        "my experience", "my opinion", "pros and cons",
        "worth it", "highly recommend", "would recommend",
        "issues after", "problems with", "been having",
        "owned for", "using for", "had for"
    ]
    
    has_ownership = any(kw in text_lower for kw in ownership_keywords)
    if has_ownership:
        score += 0.2
        logger.debug(f"Ownership keyword found in text (+0.2)")
    
    return min(score, 1.0)


def should_reject_thread(title: str, body: str, product_identity: Dict[str, Any]) -> tuple[bool, str]:
    """
    Determine if a Reddit thread should be rejected based on content analysis.
    
    Returns: (should_reject: bool, reason: str)
    """
    if not title or not isinstance(title, str):
        return True, "Empty title"
    
    combined_text = f"{title} {body or ''}".lower()
    
    # Reject keywords - strongly indicate not a product review
    reject_keywords = [
        "stock", "oos", "out of stock", "restock",
        "leak", "rumor", "rumoured", "reported",
        "target", "walmart", "bestbuy", "gamestop",
        "xbox", "microsoft",  # Usually competition context
        "sony strategy", "strategy discussion",
        "sale alert", "price drop", "discount",
        "announcement", "press release",
        "news", "report", "story",
    ]
    
    for reject_kw in reject_keywords:
        if reject_kw in combined_text:
            return True, f"Rejected: Found rejection keyword '{reject_kw}'"
    
    # Model/edition must appear in title or body
    model = product_identity.get("model", "").lower()
    keywords = product_identity.get("keywords", [])
    
    if model:
        if model not in title.lower():
            return True, f"Model '{model}' not in title"
    
    # At least one keyword must appear in title
    has_keyword_in_title = any(kw in title.lower() for kw in keywords if kw)
    if not has_keyword_in_title and model and model not in title.lower():
        return True, "No product keywords in title"
    
    # Reject if it's a question-only without context
    question_only = (
        title.endswith("?") and
        not any(phrase in combined_text for phrase in [
            "i own", "i have", "i bought", "my experience"
        ])
    )
    if question_only:
        return True, "Question-only thread without ownership context"
    
    return False, ""


def has_review_intent(text: str) -> bool:
    """
    Check if text contains evidence of review intent (ownership/experience).
    """
    if not text or not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    review_intent_keywords = [
        "i own", "i bought", "i purchased", "i have",
        "i've been using", "i've owned", "been using",
        "my experience", "my opinion", "review",
        "pros and cons", "worth it", "recommend",
        "issues", "problems with", "had issues",
        "owned for", "using for",
    ]
    
    return any(kw in text_lower for kw in review_intent_keywords)


def normalize_relevance_score(score: float) -> float:
    """Ensure relevance score is between 0.0 and 1.0."""
    return max(0.0, min(1.0, float(score)))
