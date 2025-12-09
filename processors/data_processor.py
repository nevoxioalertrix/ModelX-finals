"""Data processor for categorizing, scoring, and aggregating news articles."""

import sys
import os
from collections import Counter, defaultdict
import re
from typing import Dict, Iterable, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import CATEGORIES, CATEGORY_MIN_CONFIDENCE
from database.db_manager import DatabaseManager

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Import ML classifier
try:
    from processors.ml_classifier import get_classifier, MLClassifier
    ML_CLASSIFIER_AVAILABLE = True
except ImportError:
    ML_CLASSIFIER_AVAILABLE = False


class DataProcessor:
    """Processes news articles with configurable time windows and ML classification."""

    def __init__(self, db: Optional[DatabaseManager] = None, use_ml: bool = True):
        # Allow dependency injection for reuse/testing
        self.db = db or DatabaseManager()
        self.use_ml = use_ml and ML_CLASSIFIER_AVAILABLE
        self._ml_classifier: Optional['MLClassifier'] = None
        
        # Initialize ML classifier if available
        if self.use_ml:
            self._ml_classifier = get_classifier()
            # Auto-train if not already trained
            if not self._ml_classifier.is_trained:
                self._train_ml_model()

    def _train_ml_model(self) -> Dict:
        """Train ML model using database articles."""
        if not self._ml_classifier:
            return {'success': False, 'error': 'ML not available'}
        return self._ml_classifier.train_from_database(self.db)

    def retrain_ml_model(self) -> Dict:
        """Force retrain the ML model with current database data."""
        if not self._ml_classifier:
            return {'success': False, 'error': 'ML not available'}
        return self._ml_classifier.train_from_database(self.db)

    def get_ml_info(self) -> Dict:
        """Get ML model information."""
        if not self._ml_classifier:
            return {'ml_available': False}
        return self._ml_classifier.get_model_info()

    # ----------------------
    # Core NLP utilities
    # ----------------------
    def categorize_article(self, title: str) -> str:
        """Categorize an article using ML or keyword fallback."""
        result = self.categorize_article_with_confidence(title)
        return result[0]
    
    def categorize_article_with_confidence(self, title: str) -> Tuple[str, float]:
        """
        Categorize an article using hybrid ML + keyword approach.
        
        Uses both ML model and keyword matching, then combines results
        for more accurate classification.
        
        Returns:
            Tuple of (category, confidence_score)
        """
        # Get keyword-based result
        keyword_cat, keyword_conf = self._keyword_categorize(title)
        
        # Try ML classification if available
        ml_cat, ml_conf = None, 0.0
        if self.use_ml and self._ml_classifier and self._ml_classifier.is_trained:
            try:
                ml_cat, ml_conf = self._ml_classifier.predict(title)
            except Exception:
                pass
        
        # Hybrid decision logic
        if ml_cat and ml_conf >= 0.5:
            # ML is confident - use ML result
            if keyword_cat == ml_cat:
                # Both agree - high confidence
                return (ml_cat, min(1.0, (ml_conf + keyword_conf) / 2 + 0.2))
            elif keyword_conf >= 0.6:
                # Keyword matching is also confident - prefer keyword
                return (keyword_cat, keyword_conf)
            else:
                # Trust ML when keyword is uncertain
                return (ml_cat, ml_conf)
        elif keyword_conf >= 0.4:
            # Keyword matching has reasonable confidence
            return (keyword_cat, keyword_conf)
        elif ml_cat and ml_conf >= 0.3:
            # Low confidence ML is better than nothing
            return (ml_cat, ml_conf)
        else:
            # Both uncertain - use keyword result or general
            return (keyword_cat, keyword_conf)
    
    def _keyword_categorize(self, title: str) -> Tuple[str, float]:
        """Keyword-based categorization fallback."""
        title_lower = title.lower()
        
        category_scores: Dict[str, float] = {}
        
        for category, keywords in CATEGORIES.items():
            score = 0.0
            for keyword_entry in keywords:
                # Handle both weighted (tuple) and legacy (string) formats
                if isinstance(keyword_entry, tuple):
                    keyword, weight = keyword_entry
                else:
                    keyword, weight = keyword_entry, 1
                
                keyword_lower = keyword.lower()
                
                # Use word boundary matching to avoid partial matches
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                matches = len(re.findall(pattern, title_lower))
                
                if matches > 0:
                    score += weight * matches
            
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return ('general', 0.0)
        
        # Find best category
        best_category = max(category_scores.items(), key=lambda x: x[1])
        category_name, best_score = best_category
        
        # Calculate confidence as ratio of best score to total
        total_score = sum(category_scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.0
        
        # If confidence is too low, fall back to general
        if confidence < CATEGORY_MIN_CONFIDENCE and best_score < 3:
            return ('general', confidence)
        
        return (category_name, confidence)

    def analyze_sentiment(self, text: str) -> float:
        """Return sentiment in [-1,1]; fall back to neutral on errors/missing libs."""
        if not TEXTBLOB_AVAILABLE or not text:
            return 0.0
        try:
            blob = TextBlob(text)
            return float(blob.sentiment.polarity)  # type: ignore[union-attr]
        except Exception:
            return 0.0

    def extract_keywords(self, title: str) -> List[str]:
        """Extract keywords (>=4 letters) excluding common stop words."""
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'sri', 'lanka', 'lankan', 'says', 'said'
        }

        words = re.findall(r'\b[a-zA-Z]{4,}\b', title.lower())
        return [w for w in words if w not in stop_words]

    # ----------------------
    # Processing pipeline
    # ----------------------
    def process_articles(self) -> List[dict]:
        """Process all unprocessed articles: categorize + sentiment."""
        articles = self.db.get_unprocessed_articles()
        processed = []

        for article in articles:
            title_str = getattr(article, 'title', '') or ''
            category = self.categorize_article(title_str)
            sentiment = self.analyze_sentiment(title_str)

            self.db.mark_article_processed(getattr(article, 'id', None), category, sentiment)

            processed.append({
                'id': getattr(article, 'id', None),
                'title': title_str,
                'category': category,
                'sentiment': sentiment,
                'source': getattr(article, 'source', '') or ''
            })

        return processed

    # ----------------------
    # Time-window helpers
    # ----------------------
    def _get_articles_window(
        self,
        hours_start: float,
        hours_end: float = 0,
        sources: Optional[Iterable[str]] = None,
    ):
        """Fetch articles within (hours_start -> hours_end] window ago."""
        return self.db.get_recent_articles(hours=hours_start, hours_end=hours_end, sources=list(sources) if sources else None)

    # ----------------------
    # Analytics
    # ----------------------
    def get_trending_topics(
        self,
        hours_start: float = 168,
        hours_end: float = 0,
        sources: Optional[Iterable[str]] = None,
        top_n: int = 20,
        min_occurrences: int = 2,
    ) -> List[Tuple[str, int]]:
        """Return top keywords for the window; enforces minimum occurrence."""
        articles = self._get_articles_window(hours_start, hours_end, sources)

        keyword_counts = Counter()
        for article in articles:
            title_str = getattr(article, 'title', '') or ''
            keyword_counts.update(self.extract_keywords(title_str))

        return [(kw, cnt) for kw, cnt in keyword_counts.most_common(top_n) if cnt >= min_occurrences]

    def get_category_distribution(
        self,
        hours_start: float = 168,
        hours_end: float = 0,
        sources: Optional[Iterable[str]] = None,
    ):
        return self.db.get_category_distribution(hours=hours_start, hours_end=hours_end, sources=list(sources) if sources else None)

    def get_source_distribution(
        self,
        hours_start: float = 168,
        hours_end: float = 0,
        sources: Optional[Iterable[str]] = None,
    ):
        return self.db.get_source_distribution(hours=hours_start, hours_end=hours_end, sources=list(sources) if sources else None)

    def get_sentiment_by_category(
        self,
        hours_start: float = 168,
        hours_end: float = 0,
        sources: Optional[Iterable[str]] = None,
    ) -> dict:
        """Average sentiment per category for the window."""
        articles = self._get_articles_window(hours_start, hours_end, sources)

        sentiment_data: defaultdict = defaultdict(list)
        for article in articles:
            cat_val = getattr(article, 'category', None)
            sent_val = getattr(article, 'sentiment', None)
            if cat_val and sent_val is not None:
                sentiment_data[str(cat_val)].append(float(sent_val))

        return {cat: (sum(vals) / len(vals)) for cat, vals in sentiment_data.items() if vals}

    def close(self):
        """Close database connection."""
        self.db.close()
