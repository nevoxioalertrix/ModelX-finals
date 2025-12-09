"""
Database manager for storing and retrieving news articles and signals
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import DATABASE_PATH

Base = declarative_base()

class Article(Base):
    """Article model for storing news articles"""
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    category = Column(String(50))
    sentiment = Column(Float)
    collected_at = Column(DateTime, default=datetime.now)
    processed = Column(Integer, default=0)  # 0 = not processed, 1 = processed

class Signal(Base):
    """Signal model for storing detected signals"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True)
    signal_type = Column(String(50), nullable=False)  # risk, opportunity, trending, anomaly
    description = Column(Text, nullable=False)
    severity = Column(String(20))  # high, medium, low (for risks)
    category = Column(String(50))
    detected_at = Column(DateTime, default=datetime.now)
    meta_data = Column(Text)  # JSON string for additional data

class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, db_path=None):
        """Initialize database connection"""
        if db_path is None:
            db_path = DATABASE_PATH
        
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_article(self, title, url, source, category=None, sentiment=None):
        """Add a new article to the database"""
        try:
            article = Article(
                title=title,
                url=url,
                source=source,
                category=category,
                sentiment=sentiment
            )
            self.session.add(article)
            self.session.commit()
            return article.id
        except Exception as e:
            self.session.rollback()
            # Likely a duplicate URL
            return None
    
    def get_unprocessed_articles(self):
        """Get all articles that haven't been processed yet"""
        return self.session.query(Article).filter(Article.processed == 0).all()
    
    def mark_article_processed(self, article_id, category=None, sentiment=None):
        """Mark an article as processed"""
        article = self.session.query(Article).filter(Article.id == article_id).first()
        if article:
            setattr(article, 'processed', 1)
            if category:
                setattr(article, 'category', category)
            if sentiment is not None:
                setattr(article, 'sentiment', sentiment)
            self.session.commit()
    
    def get_recent_articles(self, hours: float = 24, hours_end: "float | None" = None, sources=None):
        """Get articles from a specific time range (supports week-based filtering)
        
        Args:
            hours: Start of range (hours ago from now) - for week ranges, this is the START (older)
            hours_end: End of range (hours ago from now) - if None, uses 0 (now)
            sources: Optional list of source names to filter by
        """
        from datetime import datetime, timedelta
        now = datetime.now()
        
        # For week-based ranges: hours_end is closer to now, hours is further back
        if hours_end is not None:
            # Normalize bounds so older >= newer; if equal, treat newer as now
            start_hours = float(hours)
            end_hours = float(hours_end)
            if start_hours < end_hours:
                start_hours, end_hours = end_hours, start_hours
            if start_hours == end_hours:
                end_hours = 0.0
            cutoff_start = now - timedelta(hours=start_hours)  # Older boundary
            cutoff_end = now - timedelta(hours=end_hours)      # Newer boundary
            query = self.session.query(Article).filter(
                Article.collected_at >= cutoff_start,
                Article.collected_at < cutoff_end
            )
        else:
            # Simple range: get all articles from last N hours
            cutoff = now - timedelta(hours=float(hours))
            query = self.session.query(Article).filter(Article.collected_at >= cutoff)
        
        if sources:
            query = query.filter(Article.source.in_(sources))
        return query.order_by(Article.collected_at.desc()).all()
    
    def get_articles_by_category(self, category, hours=24):
        """Get articles of a specific category from the last N hours (supports fractional hours)"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=float(hours))
        return self.session.query(Article).filter(
            Article.category == category,
            Article.collected_at >= cutoff
        ).order_by(Article.collected_at.desc()).all()
    
    def add_signal(self, signal_type, description, severity=None, category=None, meta_data=None):
        """Add a new signal to the database"""
        signal = Signal(
            signal_type=signal_type,
            description=description,
            severity=severity,
            category=category,
            meta_data=meta_data
        )
        self.session.add(signal)
        self.session.commit()
        return signal.id
    
    def get_recent_signals(self, signal_type=None, hours=24):
        """Get recent signals, optionally filtered by type (supports fractional hours)"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=float(hours))
        query = self.session.query(Signal).filter(Signal.detected_at >= cutoff)
        if signal_type:
            query = query.filter(Signal.signal_type == signal_type)
        return query.order_by(Signal.detected_at.desc()).all()
    
    def get_category_distribution(self, hours: float = 24, hours_end: "float | None" = None, sources=None):
        """Get distribution of articles by category (supports week-based filtering)"""
        from datetime import datetime, timedelta
        from sqlalchemy import func
        now = datetime.now()
        
        if hours_end is not None:
            start_hours = float(hours)
            end_hours = float(hours_end)
            if start_hours < end_hours:
                start_hours, end_hours = end_hours, start_hours
            if start_hours == end_hours:
                end_hours = 0.0
            cutoff_start = now - timedelta(hours=start_hours)
            cutoff_end = now - timedelta(hours=end_hours)
            query = self.session.query(Article.category, func.count(Article.id)).filter(
                Article.collected_at >= cutoff_start,
                Article.collected_at < cutoff_end,
                Article.category.isnot(None)
            )
        else:
            cutoff = now - timedelta(hours=float(hours))
            query = self.session.query(Article.category, func.count(Article.id)).filter(
                Article.collected_at >= cutoff,
                Article.category.isnot(None)
            )
        
        if sources:
            query = query.filter(Article.source.in_(sources))
        
        results = query.group_by(Article.category).all()
        return {category: count for category, count in results}
    
    def get_source_distribution(self, hours: float = 24, hours_end: "float | None" = None, sources=None):
        """Get distribution of articles by source (supports week-based filtering)"""
        from datetime import datetime, timedelta
        from sqlalchemy import func
        now = datetime.now()
        
        if hours_end is not None:
            start_hours = float(hours)
            end_hours = float(hours_end)
            if start_hours < end_hours:
                start_hours, end_hours = end_hours, start_hours
            if start_hours == end_hours:
                end_hours = 0.0
            cutoff_start = now - timedelta(hours=start_hours)
            cutoff_end = now - timedelta(hours=end_hours)
            query = self.session.query(Article.source, func.count(Article.id)).filter(
                Article.collected_at >= cutoff_start,
                Article.collected_at < cutoff_end
            )
        else:
            cutoff = now - timedelta(hours=float(hours))
            query = self.session.query(Article.source, func.count(Article.id)).filter(Article.collected_at >= cutoff)
        
        if sources:
            query = query.filter(Article.source.in_(sources))
        
        results = query.group_by(Article.source).all()
        return {source: count for source, count in results}
    
    def get_total_articles(self):
        """Get total number of articles in database"""
        return self.session.query(Article).count()
    
    def close(self):
        """Close database session"""
        self.session.close()
