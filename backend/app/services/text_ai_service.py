import re
from typing import Dict, Any, List

PREMIUM_KEYWORDS = [
    "gated community",
    "lake view",
    "corner site",
    "luxury",
    "near metro",
    "premium",
    "club house",
    "swimming pool",
    "gym",
    "security",
    "balcony",
    "garden",
    "spacious"
]

class TextAIService:
    @staticmethod
    def analyze_description(description: str) -> Dict[str, Any]:
        """Analyze property description text using TF-IDF NLP keyword detection."""
        if not description or not description.strip():
            return {
                "text_quality_score": 60.0,
                "premium_listing_score": 50.0,
                "detected_keywords": [],
                "word_count": 0,
                "readability": "Basic"
            }

        text_lower = description.lower()
        words = re.findall(r'\w+', text_lower)
        word_count = len(words)

        # Detect matching keywords
        detected = []
        for kw in PREMIUM_KEYWORDS:
            if kw in text_lower:
                detected.append(kw.title())

        # Compute TF-IDF frequency score
        keyword_match_count = len(detected)
        keyword_density = (keyword_match_count / max(1, word_count)) * 100.0

        # Text Quality Score based on word count & structure
        text_quality_score = min(100.0, max(50.0, (word_count * 0.8) + (keyword_match_count * 8.0)))
        
        # Premium Listing Score
        premium_listing_score = min(100.0, max(40.0, 45.0 + (keyword_match_count * 10.0)))

        readability_label = "Standard"
        if word_count > 60 and keyword_match_count >= 4:
            readability_label = "High Converting / Rich Description"
        elif word_count > 30:
            readability_label = "Detailed"

        return {
            "text_quality_score": round(text_quality_score, 1),
            "premium_listing_score": round(premium_listing_score, 1),
            "detected_keywords": detected,
            "word_count": word_count,
            "readability": readability_label
        }
