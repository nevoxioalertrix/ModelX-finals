"""
News scraper for collecting articles from Sri Lankan news sources
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import NEWS_SOURCES, SCRAPE_DELAY, REQUEST_TIMEOUT, MAX_ARTICLES_PER_SOURCE
from database.db_manager import DatabaseManager

class NewsScraper:
    """Scrapes news from configured sources"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_adaderana(self):
        """Scrape Ada Derana news"""
        articles = []
        try:
            response = requests.get(
                NEWS_SOURCES['adaderana']['url'],
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Try multiple selectors for Ada Derana
            news_items = soup.find_all('h2')
            if not news_items:
                news_items = soup.find_all('a', href=True)
            
            count = 0
            for item in news_items:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                try:
                    if item.name == 'h2':
                        link = item.find('a')
                        if link:
                            title = link.get_text().strip()
                            url = link.get('href', '')
                        else:
                            title = item.get_text().strip()
                            url = ''
                    else:
                        title = item.get_text().strip()
                        url = item.get('href', '')
                    
                    if title and len(title) > 20 and url:
                        url = str(url)
                        if not url.startswith('http'):
                            url = 'http://www.adaderana.lk' + url
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'Ada Derana'
                        })
                        count += 1
                except:
                    continue
        except Exception as e:
            print(f"Error scraping Ada Derana: {e}")
        
        return articles
    
    def scrape_dailymirror(self):
        """Scrape Daily Mirror news"""
        articles = []
        try:
            response = requests.get(
                NEWS_SOURCES['dailymirror']['url'],
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links that look like news articles
            all_links = soup.find_all('a', href=True)
            
            count = 0
            for link in all_links:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                try:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Filter for actual news articles
                    url = str(url) if url else ''
                    if (title and len(title) > 25 and url and 
                        ('/news/' in url or '/breaking-news/' in url or '/latest-news/' in url)):
                        if not url.startswith('http'):
                            url = 'https://www.dailymirror.lk' + url
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'Daily Mirror'
                        })
                        count += 1
                except:
                    continue
        except Exception as e:
            print(f"Error scraping Daily Mirror: {e}")
        
        return articles
    
    def scrape_newsfirst(self):
        """Scrape News First"""
        articles = []
        try:
            response = requests.get(
                NEWS_SOURCES['newsfirst']['url'],
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            count = 0
            for link in all_links:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                try:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Filter for news articles
                    url = str(url) if url else ''
                    if title and len(title) > 25 and url and '202' in url:
                        if not url.startswith('http'):
                            url = 'https://www.newsfirst.lk' + url
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'News First'
                        })
                        count += 1
                except:
                    continue
        except Exception as e:
            print(f"Error scraping News First: {e}")
        
        return articles
    
    def scrape_economynext(self):
        """Scrape Economy Next using RSS feed for reliability"""
        articles = []
        try:
            # Use RSS feed - more reliable than web scraping
            feed = feedparser.parse('https://economynext.com/feed/')
            
            seen_titles = set()
            for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
                title = entry.get('title', '').strip()
                url = entry.get('link', '')
                
                # Skip duplicates
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': 'Economy Next'
                    })
        except Exception as e:
            print(f"Error scraping Economy Next: {e}")
        
        return articles
    
    def scrape_sundaytimes(self):
        """Scrape Sunday Times"""
        articles = []
        try:
            response = requests.get(
                NEWS_SOURCES['sundaytimes']['url'],
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            count = 0
            for link in all_links:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                try:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Filter for news articles
                    url = str(url) if url else ''
                    if title and len(title) > 25 and url and ('article' in url or '202' in url):
                        if not url.startswith('http'):
                            url = 'https://www.sundaytimes.lk' + url
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'Sunday Times'
                        })
                        count += 1
                except:
                    continue
        except Exception as e:
            print(f"Error scraping Sunday Times: {e}")
        
        return articles
    
    def scrape_ceylontoday(self):
        """Scrape Ceylon Today"""
        articles = []
        try:
            response = requests.get(
                NEWS_SOURCES['ceylontoday']['url'],
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            count = 0
            for link in all_links:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                try:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Filter for news articles
                    url = str(url) if url else ''
                    if title and len(title) > 25 and url and ('202' in url or '/news/' in url or '/category/' in url):
                        if not url.startswith('http'):
                            url = 'https://ceylontoday.lk' + url
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'Ceylon Today'
                        })
                        count += 1
                except:
                    continue
        except Exception as e:
            print(f"Error scraping Ceylon Today: {e}")
        
        return articles
    
    def scrape_businesstoday(self):
        """Scrape Business Today using RSS feed for reliability"""
        articles = []
        try:
            # Use RSS feed - more reliable and no duplicates
            feed = feedparser.parse('https://businesstoday.lk/feed/')
            
            seen_titles = set()
            for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
                title = entry.get('title', '').strip()
                url = entry.get('link', '')
                
                # Skip duplicates
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': 'Business Today'
                    })
        except Exception as e:
            print(f"Error scraping Business Today: {e}")
        
        return articles
    
    def scrape_lankabusinessonline(self):
        """Scrape Lanka Business Online using RSS feed"""
        articles = []
        try:
            # Use RSS feed for reliability
            feed = feedparser.parse('https://www.lankabusinessonline.com/feed/')
            
            seen_titles = set()
            for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
                title = entry.get('title', '').strip()
                url = entry.get('link', '')
                
                # Skip duplicates
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': 'Lanka Business Online'
                    })
        except Exception as e:
            print(f"Error scraping Lanka Business Online: {e}")
        
        return articles
    
    def scrape_ft(self):
        """Scrape Financial Times (web scraping - no RSS available)"""
        articles = []
        try:
            response = requests.get(
                NEWS_SOURCES['ft']['url'],
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            seen_titles = set()
            count = 0
            for link in all_links:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                try:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Filter for news articles
                    url = str(url) if url else ''
                    if title and len(title) > 25 and url and title not in seen_titles:
                        # Check for article patterns
                        if '202' in url or '/news/' in url or '/article/' in url or '/top-story/' in url:
                            if not url.startswith('http'):
                                url = 'https://www.ft.lk' + url
                            seen_titles.add(title)
                            articles.append({
                                'title': title,
                                'url': url,
                                'source': 'Financial Times'
                            })
                            count += 1
                except:
                    continue
        except Exception as e:
            print(f"Error scraping Financial Times: {e}")
        
        return articles
    
    def scrape_newswire(self):
        """Scrape News Wire"""
        articles = []
        try:
            response = requests.get(
                NEWS_SOURCES['newswire']['url'],
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            count = 0
            for link in all_links:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                try:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Filter for news articles
                    url = str(url) if url else ''
                    if title and len(title) > 25 and url and ('202' in url or '/news/' in url or 'article' in url):
                        if not url.startswith('http'):
                            url = 'https://www.newswire.lk' + url
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'News Wire'
                        })
                        count += 1
                except:
                    continue
        except Exception as e:
            print(f"Error scraping News Wire: {e}")
        
        return articles
    
    def scrape_all(self):
        """Scrape all enabled news sources"""
        all_articles = []
        
        for source_key, source_config in NEWS_SOURCES.items():
            if not source_config['enabled']:
                continue
            
            print(f"  Scraping {source_config['name']}...")
            
            # Call appropriate scraper
            if source_key == 'adaderana':
                articles = self.scrape_adaderana()
            elif source_key == 'dailymirror':
                articles = self.scrape_dailymirror()
            elif source_key == 'newsfirst':
                articles = self.scrape_newsfirst()
            elif source_key == 'economynext':
                articles = self.scrape_economynext()
            elif source_key == 'sundaytimes':
                articles = self.scrape_sundaytimes()
            elif source_key == 'ceylontoday':
                articles = self.scrape_ceylontoday()
            elif source_key == 'businesstoday':
                articles = self.scrape_businesstoday()
            elif source_key == 'lankabusinessonline':
                articles = self.scrape_lankabusinessonline()
            elif source_key == 'ft':
                articles = self.scrape_ft()
            elif source_key == 'newswire':
                articles = self.scrape_newswire()
            else:
                articles = []
            
            # Handle None returns
            if articles is None:
                articles = []
            
            # Store in database
            new_count = 0
            for article in articles:
                article_id = self.db.add_article(
                    title=article['title'],
                    url=article['url'],
                    source=article['source']
                )
                if article_id is not None:
                    new_count += 1
            
            print(f"    Found {len(articles)} articles ({new_count} new)")
            all_articles.extend(articles)
            
            # Polite delay between sources
            time.sleep(SCRAPE_DELAY)
        
        return all_articles
    
    def close(self):
        """Close database connection"""
        self.db.close()
