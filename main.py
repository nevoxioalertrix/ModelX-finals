"""
Main runner for data collection and processing
Run this script to continuously collect and process news data
"""

import schedule
import time
from datetime import datetime
from scrapers.news_scraper import NewsScraper
from processors.data_processor import DataProcessor
from processors.signal_detector import SignalDetector

def run_collection_cycle():
    """Run one complete collection and processing cycle"""
    print(f"\n{'='*60}")
    print(f"Starting collection cycle at {datetime.now()}")
    print(f"{'='*60}")
    
    # Step 1: Scrape news
    print("\n[1/3] Scraping news sources...")
    scraper = NewsScraper()
    articles = scraper.scrape_all()
    print(f"✓ Scraped {len(articles)} articles")
    
    # Step 2: Process and categorize
    print("\n[2/3] Processing and categorizing articles...")
    processor = DataProcessor()
    processed = processor.process_articles()
    print(f"✓ Processed {len(processed)} articles")
    
    # Show category distribution
    cat_dist = processor.get_category_distribution(hours_start=24, hours_end=0)
    print("\nCategory distribution (last 24h):")
    for category, count in sorted(cat_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")
    
    processor.close()
    
    # Step 3: Detect signals
    print("\n[3/3] Detecting signals...")
    detector = SignalDetector()
    signals = detector.generate_all_signals()
    
    # Display summary
    print(f"\n{'='*60}")
    print("SIGNAL SUMMARY")
    print(f"{'='*60}")
    print(f"Risks: {len(signals['risks'])}")
    print(f"Opportunities: {len(signals['opportunities'])}")
    print(f"Trending Topics: {len(signals['trending'])}")
    print(f"Anomalies: {len(signals['anomalies'])}")
    
    if signals['risks']:
        print("\nTop Risks:")
        for risk in signals['risks'][:3]:
            print(f"  [{risk['severity'].upper()}] {risk['description']}")
    
    if signals['opportunities']:
        print("\nTop Opportunities:")
        for opp in signals['opportunities'][:3]:
            print(f"  {opp['description']}")
    
    if signals['trending']:
        print("\nTrending Now:")
        for trend in signals['trending'][:5]:
            print(f"  {trend['topic']}: {trend['count']} mentions")
    
    detector.close()
    
    print(f"\n{'='*60}")
    print(f"Cycle completed at {datetime.now()}")
    print(f"Next cycle in 30 minutes")
    print(f"{'='*60}\n")

def run_once():
    """Run collection cycle once and exit"""
    run_collection_cycle()
    print("\nSingle run completed. Exiting...")

def run_continuous():
    """Run collection cycle continuously every 30 minutes"""
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop\n")
    
    # Run immediately on start
    run_collection_cycle()
    
    # Schedule to run every 30 minutes
    schedule.every(30).minutes.do(run_collection_cycle)
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\nStopping continuous monitoring...")
        print("Goodbye!")

if __name__ == "__main__":
    import sys
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Sri Lanka Business Intelligence Platform               ║
    ║   Real-Time Situational Awareness System                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run_once()
    else:
        print("Running in continuous mode (use --once for single run)")
        run_continuous()