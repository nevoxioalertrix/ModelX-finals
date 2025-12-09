"""
Machine Learning-based article classifier using TF-IDF and Naive Bayes.
Provides more accurate categorization than keyword matching.
"""

import os
import sys
import pickle
import re
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import ML libraries
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from utils.config import CATEGORIES, BUSINESS_CATEGORIES


class MLClassifier:
    """
    Machine Learning classifier for news articles.
    Uses TF-IDF vectorization with Multinomial Naive Bayes.
    Falls back to keyword matching if ML libraries unavailable.
    """
    
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_model.pkl')
    
    def __init__(self):
        self.model: Optional[Pipeline] = None
        self.is_trained = False
        self.training_accuracy = 0.0
        self.category_labels: List[str] = []
        
        # Try to load existing model
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load pre-trained model from disk if available."""
        if not ML_AVAILABLE:
            return False
            
        if os.path.exists(self.MODEL_PATH):
            try:
                with open(self.MODEL_PATH, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.category_labels = data['labels']
                    self.training_accuracy = data.get('accuracy', 0.0)
                    self.is_trained = True
                    return True
            except Exception as e:
                print(f"Error loading model: {e}")
        return False
    
    def _save_model(self) -> bool:
        """Save trained model to disk."""
        if not self.model:
            return False
        try:
            with open(self.MODEL_PATH, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'labels': self.category_labels,
                    'accuracy': self.training_accuracy
                }, f)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for ML model."""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _generate_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Generate synthetic training data from keyword definitions.
        Creates example titles for each category based on keywords.
        """
        texts = []
        labels = []
        
        # Extensive template patterns for generating training examples
        templates = [
            "{keyword} news update for Sri Lanka",
            "Sri Lanka {keyword} report released",
            "Latest {keyword} developments announced",
            "{keyword} sector shows growth",
            "New {keyword} initiative announced by government",
            "{keyword} market trends analysis",
            "Analysis: {keyword} impact on economy",
            "{keyword} challenges and opportunities ahead",
            "Government focuses on {keyword} development",
            "{keyword} investment opportunities in Lanka",
            "Breaking: major {keyword} update",
            "{keyword} industry outlook positive",
            "Sri Lankan {keyword} sector expanding",
            "{keyword} reforms implemented",
            "Experts discuss {keyword} future",
            "{keyword} boost for Sri Lanka",
            "New {keyword} policy announced",
            "{keyword} growth exceeds expectations",
            "Sri Lanka sees {keyword} improvement",
            "{keyword} sector faces challenges",
        ]
        
        for category, keywords in CATEGORIES.items():
            for keyword_entry in keywords:
                # Handle weighted tuples
                if isinstance(keyword_entry, tuple):
                    keyword, weight = keyword_entry
                else:
                    keyword = keyword_entry
                    weight = 1.0
                
                # Generate more examples for higher-weight keywords
                num_examples = min(len(templates), max(4, int(weight * 4)))
                
                for i in range(num_examples):
                    template = templates[i % len(templates)]
                    text = template.format(keyword=keyword)
                    texts.append(self._preprocess_text(text))
                    labels.append(category)
        
        return texts, labels
    
    def train(self, additional_data: Optional[List[Tuple[str, str]]] = None) -> Dict:
        """
        Train the ML model.
        
        Args:
            additional_data: Optional list of (title, category) tuples for training
            
        Returns:
            Dictionary with training metrics
        """
        if not ML_AVAILABLE:
            return {
                'success': False,
                'error': 'scikit-learn not installed. Run: pip install scikit-learn'
            }
        
        # Generate base training data from keywords
        texts, labels = self._generate_training_data()
        
        # Add any additional real data
        if additional_data:
            for title, category in additional_data:
                texts.append(self._preprocess_text(title))
                labels.append(category)
        
        # Store unique category labels
        self.category_labels = list(set(labels))
        
        # Split data for training and validation
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Create ML pipeline
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),  # Use unigrams and bigrams
                max_features=5000,
                min_df=1,
                stop_words='english'
            )),
            ('clf', MultinomialNB(alpha=0.1))  # Smoothing parameter
        ])
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        self.training_accuracy = accuracy_score(y_test, y_pred)
        self.is_trained = True
        
        # Save model
        self._save_model()
        
        return {
            'success': True,
            'accuracy': self.training_accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'categories': len(self.category_labels)
        }
    
    def train_from_database(self, db_manager) -> Dict:
        """
        Train model using existing categorized articles from database.
        
        Args:
            db_manager: DatabaseManager instance
            
        Returns:
            Dictionary with training metrics
        """
        # Get all processed articles
        articles = db_manager.get_recent_articles(hours=720)  # 30 days
        
        additional_data = []
        for article in articles:
            title = getattr(article, 'title', '') or ''
            category = getattr(article, 'category', None)
            
            if title and category and category != 'general':
                additional_data.append((title, str(category)))
        
        return self.train(additional_data=additional_data if additional_data else None)
    
    def predict(self, title: str) -> Tuple[str, float]:
        """
        Predict category for a title.
        
        Args:
            title: Article title
            
        Returns:
            Tuple of (category, confidence)
        """
        if not ML_AVAILABLE or not self.is_trained or not self.model:
            return self._fallback_predict(title)
        
        try:
            processed = self._preprocess_text(title)
            
            # Get prediction and probability
            prediction = self.model.predict([processed])[0]
            probabilities = self.model.predict_proba([processed])[0]
            
            # Get confidence (max probability)
            confidence = float(max(probabilities))
            
            return (prediction, confidence)
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            return self._fallback_predict(title)
    
    def predict_batch(self, titles: List[str]) -> List[Tuple[str, float]]:
        """
        Predict categories for multiple titles efficiently.
        
        Args:
            titles: List of article titles
            
        Returns:
            List of (category, confidence) tuples
        """
        if not ML_AVAILABLE or not self.is_trained or not self.model:
            return [self._fallback_predict(t) for t in titles]
        
        try:
            processed = [self._preprocess_text(t) for t in titles]
            
            predictions = self.model.predict(processed)
            probabilities = self.model.predict_proba(processed)
            
            results = []
            for pred, probs in zip(predictions, probabilities):
                confidence = float(max(probs))
                results.append((pred, confidence))
            
            return results
            
        except Exception as e:
            print(f"ML batch prediction error: {e}")
            return [self._fallback_predict(t) for t in titles]
    
    def _fallback_predict(self, title: str) -> Tuple[str, float]:
        """Fallback to keyword-based prediction if ML unavailable."""
        title_lower = title.lower()
        
        category_scores: Dict[str, float] = {}
        
        for category, keywords in CATEGORIES.items():
            score = 0.0
            for keyword_entry in keywords:
                if isinstance(keyword_entry, tuple):
                    keyword, weight = keyword_entry
                else:
                    keyword, weight = keyword_entry, 1.0
                
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, title_lower))
                if matches > 0:
                    score += weight * matches
            
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return ('general', 0.0)
        
        best = max(category_scores.items(), key=lambda x: x[1])
        total = sum(category_scores.values())
        confidence = best[1] / total if total > 0 else 0.0
        
        return (best[0], confidence)
    
    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        return {
            'ml_available': ML_AVAILABLE,
            'is_trained': self.is_trained,
            'accuracy': self.training_accuracy,
            'categories': self.category_labels,
            'model_path': self.MODEL_PATH if os.path.exists(self.MODEL_PATH) else None
        }


# Singleton instance for reuse
_classifier_instance: Optional[MLClassifier] = None


def get_classifier() -> MLClassifier:
    """Get or create the singleton classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = MLClassifier()
    return _classifier_instance
