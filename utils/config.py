"""
Configuration settings for the Sri Lanka Business Intelligence Platform
"""

# News sources to scrape
NEWS_SOURCES = {
    'adaderana': {
        'url': 'http://www.adaderana.lk/news.php',
        'name': 'Ada Derana',
        'enabled': False  # General news - disabled
    },
    'dailymirror': {
        'url': 'https://www.dailymirror.lk/latest-news/159',
        'name': 'Daily Mirror',
        'enabled': False  # General news - disabled
    },
    'newsfirst': {
        'url': 'https://www.newsfirst.lk/',
        'name': 'News First',
        'enabled': False  # General news - disabled
    },
    'economynext': {
        'url': 'https://economynext.com/',
        'name': 'Economy Next',
        'enabled': True  # Business/Economy focused
    },
    'sundaytimes': {
        'url': 'https://www.sundaytimes.lk/',
        'name': 'Sunday Times',
        'enabled': False  # General news - disabled
    },
    'ceylontoday': {
        'url': 'https://ceylontoday.lk/',
        'name': 'Ceylon Today',
        'enabled': False  # General news - disabled
    },
    'businesstoday': {
        'url': 'https://businesstoday.lk/',
        'name': 'Business Today',
        'enabled': True  # Business focused
    },
    'lankabusinessonline': {
        'url': 'https://www.lankabusinessonline.com/',
        'name': 'Lanka Business Online',
        'enabled': True  # Business focused
    },
    'ft': {
        'url': 'https://www.ft.lk/',
        'name': 'Financial Times',
        'enabled': True  # Business/Finance focused
    },
    'newswire': {
        'url': 'https://www.newswire.lk/',
        'name': 'News Wire',
        'enabled': False  # General news - disabled
    }
}

# Category keyword mapping for article classification
# BUSINESS_CATEGORIES defines which categories are considered business-related
BUSINESS_CATEGORIES = ['economic', 'business', 'infrastructure', 'energy', 'technology', 'tourism', 'agriculture', 'finance']

# Minimum confidence threshold for category assignment (0.0 to 1.0)
# If confidence is below this and score is low, fall back to 'general'
CATEGORY_MIN_CONFIDENCE = 0.3

# Category weights: higher weight = stronger signal for that category
# Format: (keyword, weight) - default weight is 1.0
CATEGORIES = {
    'business': [
        ('business', 2.0), ('company', 2.0), ('corporate', 2.0), ('enterprise', 1.5), 
        ('firm', 1.5), ('industry', 1.5), ('sector', 1.0), ('startup', 2.0), 
        ('entrepreneur', 1.5), ('CEO', 2.0), ('MD', 1.5), ('chairman', 1.5), 
        ('board', 1.0), ('shareholders', 2.0), ('profit', 2.0), ('revenue', 2.0), 
        ('earnings', 2.0), ('sales', 1.5), ('turnover', 1.5), ('acquisition', 2.0), 
        ('merger', 2.0), ('IPO', 2.5), ('listing', 1.5), ('dividend', 2.0), 
        ('quarterly', 1.5), ('annual report', 2.0), ('conglomerate', 2.0),
        ('subsidiary', 1.5), ('joint venture', 2.0), ('franchise', 1.5),
        ('retail', 1.5), ('wholesale', 1.5), ('manufacturing', 1.5),
        ('supplier', 1.0), ('vendor', 1.0), ('contract', 1.0)
    ],
    'finance': [
        ('bank', 2.0), ('banking', 2.0), ('loan', 2.0), ('credit', 1.5),
        ('insurance', 2.0), ('stock', 2.0), ('shares', 2.0), ('bond', 2.0),
        ('securities', 2.0), ('forex', 2.0), ('exchange rate', 2.0),
        ('interest rate', 2.0), ('central bank', 2.5), ('CBSL', 2.5),
        ('financial', 1.5), ('capital', 1.5), ('asset', 1.5), ('equity', 2.0),
        ('fund', 1.5), ('mutual fund', 2.0), ('hedge fund', 2.0),
        ('treasury', 2.0), ('liquidity', 1.5), ('yield', 1.5)
    ],
    'economic': [
        ('economy', 2.5), ('economic', 2.0), ('inflation', 2.5), ('rupee', 2.0), 
        ('trade', 1.5), ('export', 2.0), ('import', 2.0), ('GDP', 2.5), 
        ('growth', 1.5), ('market', 1.5), ('investment', 2.0), ('budget', 2.0), 
        ('tax', 1.5), ('fiscal', 2.0), ('monetary', 2.0), ('currency', 2.0),
        ('IMF', 2.5), ('World Bank', 2.5), ('credit rating', 2.5),
        ('recession', 2.5), ('deficit', 2.0), ('surplus', 2.0),
        ('tariff', 2.0), ('subsidy', 1.5), ('privatization', 2.0),
        ('FDI', 2.5), ('remittance', 2.0), ('balance of payments', 2.5)
    ],
    'political': [
        ('government', 1.5), ('parliament', 2.0), ('minister', 1.5), 
        ('president', 1.5), ('election', 2.5), ('politics', 2.0),
        ('opposition', 2.0), ('cabinet', 2.0), ('legislation', 2.0), 
        ('policy', 1.0), ('political', 2.0), ('PM', 1.5), ('vote', 2.0),
        ('party', 1.5), ('coalition', 2.0), ('constitutional', 2.0),
        ('democracy', 1.5), ('referendum', 2.5)
    ],
    'infrastructure': [
        ('infrastructure', 2.5), ('road', 1.5), ('highway', 2.0), ('port', 2.0), 
        ('airport', 2.0), ('railway', 2.0), ('construction', 1.5),
        ('building', 1.0), ('development', 1.0), ('project', 1.0), 
        ('transport', 1.5), ('metro', 2.0), ('bridge', 1.5),
        ('expressway', 2.0), ('terminal', 1.5), ('logistics', 1.5),
        ('real estate', 2.0), ('property', 1.5), ('housing', 1.5)
    ],
    'energy': [
        ('energy', 2.0), ('power', 1.5), ('electricity', 2.0), ('fuel', 2.0), 
        ('petroleum', 2.5), ('renewable', 2.0), ('solar', 2.0),
        ('wind', 1.5), ('coal', 2.0), ('CEB', 2.5), ('power cut', 2.5), 
        ('blackout', 2.5), ('hydropower', 2.0), ('gas', 1.5), ('LNG', 2.5),
        ('oil', 2.0), ('refinery', 2.0), ('grid', 1.5)
    ],
    'agriculture': [
        ('agriculture', 2.5), ('farming', 2.0), ('crop', 2.0), ('harvest', 2.0), 
        ('fertilizer', 2.0), ('paddy', 2.0), ('tea', 2.0),
        ('rubber', 2.0), ('coconut', 2.0), ('farmer', 2.0), ('cultivation', 2.0),
        ('plantation', 2.0), ('agri', 2.0), ('fisheries', 2.0), ('livestock', 2.0),
        ('dairy', 1.5), ('organic', 1.5), ('export crop', 2.5)
    ],
    'technology': [
        ('technology', 2.0), ('digital', 1.5), ('IT', 2.0), ('tech', 1.5), 
        ('software', 2.0), ('app', 1.5), ('cyber', 2.0), ('5G', 2.5), 
        ('AI', 2.5), ('automation', 2.0), ('fintech', 2.5), ('startup', 1.5),
        ('innovation', 1.5), ('blockchain', 2.5), ('cloud', 1.5),
        ('data center', 2.0), ('e-commerce', 2.0), ('BPO', 2.0)
    ],
    'tourism': [
        ('tourism', 2.5), ('tourist', 2.0), ('hotel', 2.0), ('travel', 1.5), 
        ('visitor', 1.5), ('destination', 1.5), ('resort', 2.0),
        ('hospitality', 2.0), ('airline', 2.0), ('vacation', 1.5),
        ('arrivals', 2.0), ('leisure', 1.5), ('booking', 1.5)
    ],
    'sports': [
        ('cricket', 2.5), ('match', 1.5), ('player', 1.5), ('team', 1.0),
        ('game', 1.0), ('sports', 2.5), ('tournament', 2.0), ('hockey', 2.5),
        ('football', 2.5), ('rugby', 2.5), ('athletics', 2.0), ('olympic', 2.5),
        ('championship', 2.0), ('league', 1.5), ('cup', 1.5), ('coach', 1.5),
        ('captain', 1.5), ('innings', 2.5), ('wicket', 2.5), ('goal', 1.5),
        ('stadium', 1.5), ('fifa', 2.5), ('icc', 2.5)
    ],
    'health': [
        ('health', 2.0), ('hospital', 2.0), ('medical', 2.0), ('doctor', 1.5), 
        ('patient', 1.5), ('disease', 2.0), ('medicine', 1.5),
        ('healthcare', 2.0), ('clinic', 1.5), ('COVID', 2.5), 
        ('pandemic', 2.5), ('vaccination', 2.0), ('pharma', 2.0)
    ],
    'education': [
        ('education', 2.5), ('school', 1.5), ('university', 2.0), ('student', 1.5), 
        ('teacher', 1.5), ('exam', 2.0), ('college', 1.5),
        ('academic', 1.5), ('learning', 1.0), ('educational', 2.0),
        ('scholarship', 2.0), ('campus', 1.5), ('degree', 1.5)
    ],
    'environment': [
        ('environment', 2.5), ('climate', 2.0), ('pollution', 2.0), ('forest', 1.5), 
        ('wildlife', 2.0), ('conservation', 2.0),
        ('green', 1.0), ('sustainable', 1.5), ('eco', 1.5), ('carbon', 2.0), 
        ('flood', 2.0), ('drought', 2.0), ('disaster', 2.0),
        ('cyclone', 2.5), ('tsunami', 2.5), ('landslide', 2.0)
    ],
    'security': [
        ('security', 1.5), ('police', 1.5), ('crime', 2.0), ('arrest', 2.0), 
        ('military', 2.0), ('army', 2.0), ('navy', 2.0), ('force', 1.0),
        ('law', 1.0), ('justice', 1.5), ('court', 1.5), ('legal', 1.0), 
        ('investigation', 1.5), ('terrorism', 2.5), ('defense', 2.0)
    ],
    'social': [
        ('protest', 2.0), ('strike', 2.0), ('demonstration', 2.0), ('rally', 2.0), 
        ('social', 1.0), ('community', 1.0), ('public', 1.0),
        ('civil', 1.5), ('rights', 1.5), ('welfare', 1.5), ('poverty', 2.0), 
        ('unemployment', 2.0), ('labour', 1.5), ('union', 1.5)
    ]
}

# Risk signal keywords
RISK_KEYWORDS = {
    'high': [
        'crisis', 'emergency', 'collapse', 'disaster', 'shortage', 'critical',
        'emergency', 'breakdown', 'failure', 'default', 'bankrupt'
    ],
    'medium': [
        'protest', 'strike', 'disruption', 'delay', 'concern', 'warning', 'risk',
        'threat', 'decline', 'drop', 'fall', 'decrease', 'suspend'
    ],
    'low': [
        'issue', 'problem', 'challenge', 'difficulty', 'slow', 'weak', 'uncertain'
    ]
}

# Opportunity signal keywords
OPPORTUNITY_KEYWORDS = [
    'launch', 'open', 'expand', 'growth', 'increase', 'rise', 'boost', 'improve',
    'development', 'investment', 'new', 'innovation', 'opportunity', 'success',
    'agreement', 'deal', 'partnership', 'collaboration', 'export', 'record'
]

# Scraping settings
SCRAPE_DELAY = 2  # Seconds between requests to the same source
REQUEST_TIMEOUT = 10  # Seconds to wait for response
MAX_ARTICLES_PER_SOURCE = 50  # Maximum articles to fetch per source

# Database settings
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'sri_lanka_intel.db')

# Signal detection thresholds
TRENDING_THRESHOLD = 3  # Minimum mentions to be considered trending
ANOMALY_MULTIPLIER = 2.5  # Activity must be X times normal to be anomalous
SIGNAL_LOOKBACK_HOURS = 24  # Hours to look back for signal detection
