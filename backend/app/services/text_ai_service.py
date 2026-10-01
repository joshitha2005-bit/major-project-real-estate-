import os
import re
import pickle
import numpy as np
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")
VECTORIZER_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")

PREMIUM_KEYWORDS = [
    "gated community", "lake view", "corner site", "luxury", "near metro",
    "premium", "club house", "swimming pool", "gym", "security",
    "balcony", "garden", "spacious"
]

POSITIVE_LEXICON = {
    "luxury", "premium", "spacious", "modern", "prime", "excellent",
    "beautiful", "stunning", "grand", "peaceful", "panoramic", "brand new",
    "high quality", "well maintained", "delightful", "exclusive", "vibrant",
    "convenient", "modular", "covered", "woodwork", "fitted"
}

NEGATIVE_LEXICON = {
    "old", "damaged", "dilapidated", "noisy", "cramped", "poor", "leakage",
    "small", "congested", "dark", "unfurnished", "outdated", "remote"
}

AMENITY_CATEGORIES = {
    "Luxury & Finishes": [
        ("luxury", "Luxury"),
        ("premium", "Premium Finishes"),
        ("modular kitchen", "Modular Kitchen"),
        ("wooden flooring", "Wooden Flooring"),
        ("woodwork", "Interior Woodwork"),
        ("modern interior", "Modern Interiors"),
        ("modern", "Modern Design"),
        ("marble", "Marble Flooring"),
        ("penthouse", "Penthouse"),
        ("duplex", "Duplex Layout")
    ],
    "Security & Infrastructure": [
        ("24/7 security", "24/7 Security"),
        ("security", "Security System"),
        ("cctv", "CCTV Surveillance"),
        ("power backup", "Power Backup"),
        ("gated community", "Gated Community"),
        ("covered parking", "Covered Parking"),
        ("parking", "Parking Space"),
        ("lift", "Elevator / Lift"),
        ("intercom", "Intercom Facility")
    ],
    "Location & Connectivity": [
        ("metro", "Metro Connectivity"),
        ("highway", "Highway Access"),
        ("airport", "Airport Connectivity"),
        ("school", "Near Schools"),
        ("schools", "Near Schools"),
        ("hospital", "Near Hospitals"),
        ("hospitals", "Near Hospitals"),
        ("it park", "IT Park Nearby"),
        ("tech park", "Tech Park Nearby"),
        ("prime", "Prime Location"),
        ("main road", "Main Road Access")
    ],
    "Amenities": [
        ("swimming pool", "Swimming Pool"),
        ("gym", "Gymnasium"),
        ("clubhouse", "Clubhouse"),
        ("club house", "Clubhouse"),
        ("garden", "Landscaped Garden"),
        ("park", "Park View"),
        ("balcony", "Private Balcony"),
        ("play area", "Children's Play Area"),
        ("tennis court", "Sports Court")
    ]
}

class TextAIService:
    _vectorizer = None

    @classmethod
    def _preprocess_text(cls, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @classmethod
    def _get_vectorizer(cls) -> TfidfVectorizer:
        if cls._vectorizer is not None:
            return cls._vectorizer

        os.makedirs(MODELS_DIR, exist_ok=True)
        if os.path.exists(VECTORIZER_PATH):
            try:
                with open(VECTORIZER_PATH, "rb") as f:
                    cls._vectorizer = pickle.load(f)
                return cls._vectorizer
            except Exception as e:
                print(f"Failed to load vectorizer from pickle: {e}")

        # Build corpus from database seed properties
        corpus = []
        try:
            from app.services.seed_service import SEEDED_PROPERTIES
            corpus = [p["description"] for p in SEEDED_PROPERTIES if p.get("description")]
        except Exception:
            pass

        if not corpus or len(corpus) < 5:
            corpus = [
                "Premium Apartment in prime Koramangala built by Sobha. Features 2 BHK spacious layout, modern interior woodwork, 24/7 security, power backup, covered parking, and close access to schools, hospitals, and Metro connectivity.",
                "Luxury Villa in Indiranagar with swimming pool, private garden, gym, clubhouse, gated community, CCTV surveillance, and 4 BHK grand layout.",
                "Standard 2BHK flat in Whitefield near IT park, basic amenities, covered parking, lift access, water supply, and security.",
                "Spacious 3BHK penthouse near Electronic City with lake view, modular kitchen, wooden flooring, and 24/7 power backup."
            ]

        processed_corpus = [cls._preprocess_text(doc) for doc in corpus if doc]
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000, ngram_range=(1, 2))
        vectorizer.fit(processed_corpus)
        cls._vectorizer = vectorizer

        try:
            with open(VECTORIZER_PATH, "wb") as f:
                pickle.dump(vectorizer, f)
        except Exception as e:
            print(f"Failed to save vectorizer pickle: {e}")

        return cls._vectorizer

    @classmethod
    def extract_text_feature_vector(cls, description: str, n_features: int = 16) -> np.ndarray:
        """
        Extract numeric TF-IDF feature vector of fixed length n_features (default 16).
        Returns np.ndarray of shape (n_features,) float32.
        """
        import numpy as np
        if not description or not isinstance(description, str) or not description.strip():
            return np.zeros(n_features, dtype=np.float32)

        try:
            vec = cls._get_vectorizer()
            clean_text = cls._preprocess_text(description)
            tfidf_mat = vec.transform([clean_text])
            dense = tfidf_mat.toarray()[0]
            
            if len(dense) >= n_features:
                feat = dense[:n_features]
            else:
                feat = np.zeros(n_features, dtype=np.float32)
                feat[:len(dense)] = dense
                
            return feat.astype(np.float32)
        except Exception as e:
            print(f"Error in extract_text_feature_vector: {e}")
            return np.zeros(n_features, dtype=np.float32)

    @classmethod
    def _extract_top_tfidf(cls, description: str, top_n: int = 8) -> List[Dict[str, Any]]:
        if not description or not description.strip():
            return []
        try:
            vec = cls._get_vectorizer()
            clean_text = cls._preprocess_text(description)
            if not clean_text:
                return []
            transformed = vec.transform([clean_text])
            scores = transformed.toarray()[0]
            feature_names = vec.get_feature_names_out()

            non_zero_indices = scores.argsort()[::-1]
            top_terms = []
            for idx in non_zero_indices:
                score = scores[idx]
                if score <= 0:
                    break
                term = feature_names[idx]
                if term.isdigit():
                    continue
                top_terms.append({
                    "term": term,
                    "weight": round(float(score), 2)
                })
                if len(top_terms) >= top_n:
                    break
            return top_terms
        except Exception as e:
            print(f"TF-IDF extraction error: {e}")
            return []

    @classmethod
    def _analyze_sentiment_and_tone(cls, text: str, word_count: int) -> Dict[str, Any]:
        if not text or word_count == 0:
            return {
                "sentiment_score": 0.50,
                "sentiment_label": "Neutral",
                "tone": "Neutral"
            }

        text_lower = text.lower()
        tokens = set(re.findall(r'\w+', text_lower))

        pos_matches = len(tokens.intersection(POSITIVE_LEXICON))
        neg_matches = len(tokens.intersection(NEGATIVE_LEXICON))

        base_score = 0.50 + (pos_matches * 0.08) - (neg_matches * 0.15)
        sentiment_score = min(1.00, max(0.00, round(base_score, 2)))

        if sentiment_score >= 0.65:
            sentiment_label = "Positive"
        elif sentiment_score >= 0.45:
            sentiment_label = "Neutral"
        else:
            sentiment_label = "Negative"

        if sentiment_score >= 0.70 and word_count >= 25:
            tone = "Enthusiastic"
        elif word_count >= 30 and sentiment_score >= 0.50:
            tone = "Professional"
        elif word_count >= 10:
            tone = "Neutral"
        else:
            tone = "Low Quality"

        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "tone": tone
        }

    @classmethod
    def _extract_categorized_amenities(cls, text: str) -> Dict[str, List[str]]:
        if not text:
            return {
                "Luxury & Finishes": [],
                "Security & Infrastructure": [],
                "Location & Connectivity": [],
                "Amenities": []
            }

        text_lower = text.lower()
        result = {}

        for category, item_list in AMENITY_CATEGORIES.items():
            matched = []
            seen_labels = set()
            for kw, label in item_list:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text_lower) and label not in seen_labels:
                    matched.append(label)
                    seen_labels.add(label)
            result[category] = matched

        return result

    @classmethod
    def analyze_description(cls, description: str) -> Dict[str, Any]:
        """Analyze property description text using TF-IDF, Sentiment, and Feature Extraction NLP."""
        if not description or not description.strip():
            return {
                "text_available": False,
                "status": "TEXT DATA UNAVAILABLE",
                "text_quality_score": 60.0,
                "premium_listing_score": 50.0,
                "detected_keywords": [],
                "word_count": 0,
                "readability": "Basic",
                "sentiment_score": 0.50,
                "sentiment_label": "Neutral",
                "tone": "Neutral",
                "top_tfidf_terms": [],
                "categorized_amenities": {
                    "Luxury & Finishes": [],
                    "Security & Infrastructure": [],
                    "Location & Connectivity": [],
                    "Amenities": []
                }
            }

        text_lower = description.lower()
        words = re.findall(r'\w+', text_lower)
        word_count = len(words)

        # Detect matching keywords
        detected = []
        for kw in PREMIUM_KEYWORDS:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                detected.append(kw.title())

        # Extract TF-IDF terms
        top_tfidf_terms = cls._extract_top_tfidf(description, top_n=8)

        # Sentiment and tone
        sent_info = cls._analyze_sentiment_and_tone(description, word_count)

        # Categorized Amenities
        categorized_amenities = cls._extract_categorized_amenities(description)
        total_amenities = sum(len(items) for items in categorized_amenities.values())

        # Quality and Premium Scores
        tfidf_weight_sum = sum(t["weight"] for t in top_tfidf_terms)
        text_quality_score = min(100.0, max(30.0, (word_count * 0.5) + (tfidf_weight_sum * 15.0) + (total_amenities * 4.0) + (sent_info["sentiment_score"] * 20.0)))
        premium_listing_score = min(100.0, max(20.0, 35.0 + (len(categorized_amenities.get("Luxury & Finishes", [])) * 12.0) + (len(categorized_amenities.get("Security & Infrastructure", [])) * 8.0) + (sent_info["sentiment_score"] * 25.0)))

        # Readability label
        if word_count > 50 and text_quality_score >= 75.0:
            readability_label = "High Converting / Rich Description"
        elif word_count > 25:
            readability_label = "Detailed"
        elif word_count > 10:
            readability_label = "Standard"
        else:
            readability_label = "Basic"

        return {
            "text_available": True,
            "status": "TEXT DATA AVAILABLE",
            "text_quality_score": round(text_quality_score, 1),
            "premium_listing_score": round(premium_listing_score, 1),
            "detected_keywords": detected,
            "word_count": word_count,
            "readability": readability_label,
            "sentiment_score": sent_info["sentiment_score"],
            "sentiment_label": sent_info["sentiment_label"],
            "tone": sent_info["tone"],
            "top_tfidf_terms": top_tfidf_terms,
            "categorized_amenities": categorized_amenities
        }

