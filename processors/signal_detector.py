"""
Signal detector for identifying risks, opportunities, trends, and anomalies
"""

import sys
import os
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Iterable, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import RISK_KEYWORDS, OPPORTUNITY_KEYWORDS, TRENDING_THRESHOLD, ANOMALY_MULTIPLIER, SIGNAL_LOOKBACK_HOURS
from database.db_manager import DatabaseManager
from processors.data_processor import DataProcessor


def _keyword_matches(keyword: str, text: str) -> bool:
    """Check if keyword matches in text using word boundaries."""
    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
    return bool(re.search(pattern, text.lower()))


class SignalDetector:
    """Detects signals from processed news data"""
    
    def __init__(self, db: Optional[DatabaseManager] = None, processor: Optional[DataProcessor] = None):
        self.db = db or DatabaseManager()
        self.processor = processor or DataProcessor(db=self.db)
    
    def detect_risks(self, hours_start: float = SIGNAL_LOOKBACK_HOURS, hours_end: float = 0, sources: Optional[Iterable[str]] = None):
        """Detect risk signals from articles within the window."""
        articles = self.db.get_recent_articles(hours=hours_start, hours_end=hours_end, sources=list(sources) if sources else None)
        risks = []
        
        for article in articles:
            title_str = getattr(article, 'title', '') or ''
            cat_str = getattr(article, 'category', None) or 'general'
            source_str = getattr(article, 'source', '') or ''
            url_str = getattr(article, 'url', '') or ''
            
            # Check for high severity keywords with word boundaries
            for keyword in RISK_KEYWORDS['high']:
                if _keyword_matches(keyword, title_str):
                    risks.append({
                        'severity': 'high',
                        'description': title_str,
                        'category': str(cat_str),
                        'source': str(source_str),
                        'url': str(url_str),
                        'detected_at': getattr(article, 'collected_at', None)
                    })
                    break
            else:
                # Check for medium severity
                for keyword in RISK_KEYWORDS['medium']:
                    if _keyword_matches(keyword, title_str):
                        risks.append({
                            'severity': 'medium',
                            'description': title_str,
                            'category': str(cat_str),
                            'source': str(source_str),
                            'url': str(url_str),
                            'detected_at': getattr(article, 'collected_at', None)
                        })
                        break
                else:
                    # Check for low severity
                    for keyword in RISK_KEYWORDS['low']:
                        if _keyword_matches(keyword, title_str):
                            risks.append({
                                'severity': 'low',
                                'description': title_str,
                                'category': str(cat_str),
                                'source': str(source_str),
                                'url': str(url_str),
                                'detected_at': getattr(article, 'collected_at', None)
                            })
                            break
        
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        risks.sort(key=lambda x: severity_order[x['severity']])
        
        return risks
    
    def detect_opportunities(self, hours_start: float = SIGNAL_LOOKBACK_HOURS, hours_end: float = 0, sources: Optional[Iterable[str]] = None):
        """Detect opportunity signals from articles within the window."""
        articles = self.db.get_recent_articles(hours=hours_start, hours_end=hours_end, sources=list(sources) if sources else None)
        opportunities = []
        
        for article in articles:
            title_str = getattr(article, 'title', '') or ''
            cat_str = getattr(article, 'category', None) or 'general'
            source_str = getattr(article, 'source', '') or ''
            url_str = getattr(article, 'url', '') or ''
            sent_raw = getattr(article, 'sentiment', None)
            sent_val = float(sent_raw) if sent_raw is not None else 0.0
            
            # Check for opportunity keywords with word boundaries
            for keyword in OPPORTUNITY_KEYWORDS:
                if _keyword_matches(keyword, title_str):
                    opportunities.append({
                        'description': title_str,
                        'category': str(cat_str),
                        'source': str(source_str),
                        'url': str(url_str),
                        'detected_at': getattr(article, 'collected_at', None),
                        'sentiment': sent_val
                    })
                    break
        
        # Sort by sentiment (most positive first)
        opportunities.sort(key=lambda x: x['sentiment'], reverse=True)
        
        return opportunities
    
    def detect_trending_topics(self, hours_start: float = SIGNAL_LOOKBACK_HOURS, hours_end: float = 0, sources: Optional[Iterable[str]] = None):
        """Detect trending topics within the window."""
        trending_keywords = self.processor.get_trending_topics(hours_start=hours_start, hours_end=hours_end, sources=sources)
        
        trending = []
        for keyword, count in trending_keywords:
            if count >= TRENDING_THRESHOLD:
                trending.append({
                    'topic': keyword,
                    'count': count,
                    'timeframe': f'{hours_start}h->{hours_end}h'
                })
        
        return trending
    
    def detect_anomalies(self, hours_recent: float = 1, hours_baseline: float = 24):
        """Detect anomalies in news activity using recent vs baseline windows."""
        anomalies = []
        
        # Get article counts for different time periods
        recent_articles = self.db.get_recent_articles(hours=hours_recent)
        baseline_articles = self.db.get_recent_articles(hours=hours_baseline)
        
        recent_count = len(recent_articles)
        baseline_avg = len(baseline_articles) / 24  # Average per hour
        
        # Check if recent activity is anomalously high
        if recent_count > baseline_avg * ANOMALY_MULTIPLIER:
            anomalies.append({
                'type': 'high_volume',
                'description': f'Unusual spike in news activity: {recent_count} articles in last hour (avg: {baseline_avg:.1f}/hour)',
                'severity': 'medium',
                'detected_at': datetime.now()
            })
        
        # Check for category-specific anomalies
        cat_dist = self.db.get_category_distribution(hours=hours_recent)
        baseline_dist = self.db.get_category_distribution(hours=hours_baseline)
        
        for category, count in cat_dist.items():
            baseline_count = baseline_dist.get(category, 0) / 24
            if count > baseline_count * ANOMALY_MULTIPLIER and count >= 3:
                anomalies.append({
                    'type': 'category_spike',
                    'description': f'Spike in {category} news: {count} articles in last hour',
                    'category': category,
                    'severity': 'low',
                    'detected_at': datetime.now()
                })
        
        return anomalies
    
    def generate_all_signals(self):
        """Generate all types of signals"""
        return {
            'risks': self.detect_risks(),
            'opportunities': self.detect_opportunities(),
            'trending': self.detect_trending_topics(),
            'anomalies': self.detect_anomalies()
        }
    
    def close(self):
        """Close database connection"""
        self.db.close()
        self.processor.close()
