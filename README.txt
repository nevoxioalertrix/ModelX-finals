================================================================================
        SRI LANKA BUSINESS INTELLIGENCE PLATFORM
        Real-Time Situational Awareness System
================================================================================

OVERVIEW
--------
This platform provides real-time business intelligence for Sri Lanka by:
- Scraping news from 4 major Sri Lankan business news sources
- Categorizing articles using ML (TF-IDF + Naive Bayes) with 87.6% accuracy
- Detecting risks and opportunities automatically
- Providing interactive dashboards with auto-refresh capability

NEWS SOURCES
------------
1. Economy Next (economynext.com)
2. Business Today (businesstoday.lk)
3. Lanka Business Online (lankabusinessonline.com)
4. Financial Times Sri Lanka (ft.lk)

================================================================================
                            SETUP GUIDE
================================================================================

PREREQUISITES
-------------
- Python 3.9 or higher installed
- Internet connection for scraping news

--------------------------------------------------------------------------------
METHOD 1: EASY SETUP  (Double-Click and Run the RUN_DASHBOARD to install venv automatically)
--------------------------------------------------------------------------------

STEP 1: Create the Virtual Environment
---------------------------------------
Option A - Using Command Prompt:
   1. Open Command Prompt (Win + R, type "cmd", press Enter)
   2. Navigate to the src folder:
      cd C:\path\to\sri-lanka-business-intel\src
   3. Create virtual environment:
      python -m venv .venv
   4. Activate it:
      .venv\Scripts\activate
   5. Install dependencies:
      pip install -r requirements.txt

Option B - Using PowerShell:
   1. Open PowerShell
   2. Navigate to the src folder:
      cd C:\path\to\sri-lanka-business-intel\src
   3. Create virtual environment:
      python -m venv .venv
   4. Activate it:
      .venv\Scripts\Activate.ps1
   5. Install dependencies:
      pip install -r requirements.txt

STEP 2: Create a Launcher File (Run Without Terminal)
------------------------------------------------------
Create a file named "RUN_DASHBOARD.bat" in the src folder with this content:

   @echo off
   cd /d "%~dp0"
   call .venv\Scripts\activate.bat
   start http://localhost:8501
   python -m streamlit run app.py --server.headless true
   pause

Then simply DOUBLE-CLICK "RUN_DASHBOARD.bat" to launch the dashboard!
The browser will open automatically.

--------------------------------------------------------------------------------
METHOD 2: MANUAL TERMINAL SETUP
--------------------------------------------------------------------------------

1. Open Terminal/Command Prompt
2. Navigate to src folder:
   cd C:\path\to\sri-lanka-business-intel\src

3. Create virtual environment (first time only):
   python -m venv .venv

4. Activate virtual environment:
   Windows CMD:     .venv\Scripts\activate.bat
   Windows PS:      .venv\Scripts\Activate.ps1
   Linux/Mac:       source .venv/bin/activate

5. Install dependencies (first time only):
   pip install -r requirements.txt

6. Run the dashboard:
   streamlit run app.py 
   
(cd "c:\Users\humai\Desktop\sri-lanka-business-intel\src"; ..\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true) this is the command i used to run app.py

7. Open browser and go to: http://localhost:8501

================================================================================
                         USING THE DASHBOARD
================================================================================

SIDEBAR CONTROLS
----------------
- Time Window: Select analysis period (6 hours to 30 days)
- News Sources: Filter by specific sources
- Refresh Data: Manually refresh the dashboard
- Run Collection: Scrape new articles from all sources
- Retrain ML Model: Retrain the classifier with new data

AUTO-REFRESH
------------
- Enable "Auto-refresh" in the sidebar
- Select interval (1 min to 1 hour)
- Enable "Auto-collect" to scrape new articles automatically

MAIN DASHBOARD SECTIONS
-----------------------
1. Key Performance Indicators (KPIs)
   - Total articles, risks, opportunities, active sources

2. National Activity Indicators
   - Category distribution chart
   - Trending topics

3. Strategic Intelligence Summary
   - Risk signals with severity levels
   - Business opportunities

4. Operational Environment Intelligence
   - Per-source article feeds
   - Latest news with sentiment analysis
   - Activity timeline
   - Deep analysis charts

================================================================================
                         FILE STRUCTURE
================================================================================

src/
├── app.py              - Main Streamlit dashboard (run this)
├── main.py             - Alternative entry point
├── scheduler.py        - Background collection scheduler
├── requirements.txt    - Python dependencies
├── README.txt          - This file
├── .gitignore          - Git ignore rules
│
├── database/
│   ├── __init__.py
│   └── db_manager.py   - SQLite database manager
│
├── processors/
│   ├── __init__.py
│   ├── data_processor.py    - Article processing & categorization
│   ├── ml_classifier.py     - TF-IDF + Naive Bayes ML model
│   └── signal_detector.py   - Risk & opportunity detection
│
├── scrapers/
│   ├── __init__.py
│   └── news_scraper.py      - RSS feed scraper
│
└── utils/
    ├── __init__.py
    └── config.py            - Source configuration

================================================================================
                         DEPENDENCIES
================================================================================

Main packages (from requirements.txt):
- streamlit>=1.28.0          - Web dashboard framework
- streamlit-autorefresh       - Auto-refresh functionality
- pandas                      - Data manipulation
- plotly                      - Interactive charts
- sqlalchemy                  - Database ORM
- feedparser                  - RSS feed parsing
- requests                    - HTTP requests
- beautifulsoup4              - HTML parsing
- textblob                    - Sentiment analysis
- scikit-learn                - Machine learning
- nltk                        - Natural language processing

================================================================================
                         TROUBLESHOOTING
================================================================================

Problem: "python" command not found
Solution: Add Python to your system PATH or use full path like:
          C:\Python311\python.exe -m venv .venv

Problem: pip install fails
Solution: Upgrade pip first:
          python -m pip install --upgrade pip

Problem: Streamlit won't start
Solution: Make sure virtual environment is activated (you should see
          (.venv) at the start of your command prompt)

Problem: No articles showing
Solution: Click "Run Collection" button to scrape new articles

Problem: Port 8501 already in use
Solution: Either close the other instance or run with different port:
          streamlit run app.py --server.port 8502

Problem: ML Model accuracy is low
Solution: Click "Retrain ML Model" after collecting more articles

================================================================================
                         BACKGROUND SCHEDULER
================================================================================

To run continuous data collection in the background:

1. Open a new terminal
2. Navigate to src folder
3. Activate virtual environment
4. Run: python scheduler.py --interval 15

This will collect new articles every 15 minutes automatically.

Options:
  --interval MINUTES   Set collection interval (default: 15)
  --once               Run once and exit

================================================================================
                              CONTACT
================================================================================

For issues or questions, please contact the development team.

================================================================================
                           END OF README
================================================================================
