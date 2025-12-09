"""
Background Scheduler for Sri Lanka Business Intelligence Platform
Runs continuously to collect news articles at regular intervals.

Usage:
    python scheduler.py                    # Run with default 30 minute interval
    python scheduler.py --interval 15      # Run every 15 minutes
    python scheduler.py --interval 60      # Run every 60 minutes (1 hour)
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.db_manager import DatabaseManager
from processors.data_processor import DataProcessor
from processors.signal_detector import SignalDetector
from scrapers.news_scraper import NewsScraper
from utils.config import NEWS_SOURCES


def get_enabled_sources():
    """Get list of enabled source names."""
    return [config['name'] for key, config in NEWS_SOURCES.items() if config.get('enabled', False)]


def run_collection():
    """Run a single collection cycle."""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting collection cycle...")
    print(f"{'='*60}")
    
    try:
        # Step 1: Scrape articles
        print("\n[1/3] Scraping news sources...")
        scraper = NewsScraper()
        articles = scraper.scrape_all()
        scraper.close()
        
        # Count by source
        source_counts = {}
        for art in articles:
            src = art.get('source', 'Unknown')
            source_counts[src] = source_counts.get(src, 0) + 1
        
        print(f"      Scraped {len(articles)} articles:")
        for src, cnt in sorted(source_counts.items()):
            print(f"        - {src}: {cnt}")
        
        # Step 2: Process articles
        print("\n[2/3] Processing and categorizing articles...")
        db = DatabaseManager()
        processor = DataProcessor(db=db)
        processed = processor.process_articles()
        print(f"      Processed {len(processed)} new articles")
        
        # Step 3: Detect signals
        print("\n[3/3] Detecting signals...")
        detector = SignalDetector(db=db, processor=processor)
        signals = detector.generate_all_signals()
        print(f"      Detected signals:")
        print(f"        - Risks: {len(signals['risks'])}")
        print(f"        - Opportunities: {len(signals['opportunities'])}")
        print(f"        - Trending: {len(signals['trending'])}")
        
        # Summary
        total = db.get_total_articles()
        enabled = get_enabled_sources()
        recent_24h = len(db.get_recent_articles(hours=24, sources=enabled))
        
        print(f"\n{'='*60}")
        print(f"Collection complete!")
        print(f"  Total articles in DB: {total}")
        print(f"  Articles in last 24h: {recent_24h}")
        print(f"{'='*60}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Collection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_scheduler(interval_minutes: int = 30):
    """Run the scheduler continuously."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║   Sri Lanka Business Intelligence - Background Scheduler     ║
║   Real-Time News Collection System                          ║
╚══════════════════════════════════════════════════════════════╝

Configuration:
  - Collection interval: {interval_minutes} minutes
  - Enabled sources: {', '.join(get_enabled_sources())}
  
Press Ctrl+C to stop the scheduler.
""")
    
    collection_count = 0
    
    while True:
        try:
            collection_count += 1
            print(f"\n[Collection #{collection_count}]")
            
            success = run_collection()
            
            if success:
                print(f"\nNext collection in {interval_minutes} minutes...")
            else:
                print(f"\nRetrying in {interval_minutes} minutes...")
            
            # Sleep until next collection
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            print("\n\nScheduler stopped by user.")
            break
        except Exception as e:
            print(f"\n[ERROR] Scheduler error: {e}")
            print(f"Retrying in {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Background scheduler for news collection'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Collection interval in minutes (default: 30)'
    )
    parser.add_argument(
        '--once', '-o',
        action='store_true',
        help='Run collection once and exit'
    )
    
    args = parser.parse_args()
    
    if args.once:
        print("Running single collection...")
        run_collection()
    else:
        run_scheduler(interval_minutes=args.interval)


if __name__ == '__main__':
    main()
