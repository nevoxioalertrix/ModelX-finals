"""
Streamlit Dashboard for Sri Lanka Business Intelligence Platform
Run with: streamlit run app.py
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from database.db_manager import DatabaseManager
from processors.data_processor import DataProcessor
from processors.signal_detector import SignalDetector
from scrapers.news_scraper import NewsScraper
from utils.config import NEWS_SOURCES

# Page configuration
st.set_page_config(
    page_title="Sri Lanka Business Intelligence",
    page_icon="🇱🇰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 5 minutes for real-time updates
AUTO_REFRESH_INTERVAL = 300  # seconds

# Custom CSS - Professional UI with Corporate Color Palette
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-navy: #1a365d;
        --primary-blue: #2563eb;
        --accent-teal: #0891b2;
        --success-green: #059669;
        --warning-amber: #d97706;
        --danger-red: #dc2626;
        --neutral-50: #f8fafc;
        --neutral-100: #f1f5f9;
        --neutral-200: #e2e8f0;
        --neutral-700: #334155;
        --neutral-800: #1e293b;
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main {
        background: linear-gradient(-45deg, #1e3a8a, #2563eb, #3b82f6, #60a5fa, #0ea5e9);
        background-size: 400% 400%;
        animation: gradientFlow 30s ease infinite;
        position: relative;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 20% 80%, rgba(37, 99, 235, 0.2) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.2) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes glassShimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.9) 0%, rgba(37, 99, 235, 0.85) 100%);
        backdrop-filter: blur(30px) saturate(180%) brightness(0.8);
        -webkit-backdrop-filter: blur(30px) saturate(180%) brightness(0.8);
        padding: 25px 30px;
        border-radius: 20px;
        margin-bottom: 16px;
        box-shadow: 0 12px 40px 0 rgba(30, 58, 138, 0.7),
                    0 0 40px rgba(59, 130, 246, 0.6),
                    inset 0 2px 0 0 rgba(255, 255, 255, 0.3),
                    inset 0 -2px 0 0 rgba(30, 58, 138, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.3);
        text-align: center;
        animation: fadeIn 0.8s ease-out, float 10s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .hero-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        background-size: 200% 100%;
        animation: glassShimmer 8s ease-in-out infinite;
        pointer-events: none;
    }
    
    .hero-title {
        color: #ffffff !important;
        font-size: 42px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 8px 32px rgba(0,0,0,1), 0 4px 16px rgba(0,0,0,1), 0 2px 8px rgba(0,0,0,0.95), 0 0 40px rgba(255, 255, 255, 0.9), 0 0 80px rgba(255, 255, 255, 0.6);
        filter: drop-shadow(0 0 40px rgba(255, 255, 255, 0.8)) brightness(1.2);
        -webkit-text-stroke: 0.5px rgba(255, 255, 255, 0.8);
    }
    
    .hero-subtitle {
        color: #ffffff !important;
        font-size: 17px;
        font-weight: 500;
        margin-top: 12px;
        letter-spacing: 0.5px;
        text-shadow: 0 6px 20px rgba(0,0,0,1), 0 3px 10px rgba(0,0,0,0.95), 0 0 30px rgba(255, 255, 255, 0.8), 0 0 60px rgba(255, 255, 255, 0.5);
        filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.7)) brightness(1.15);
    }
    
    @keyframes liquidMove {
        0%, 100% { border-radius: 20px 25px 20px 25px; }
        50% { border-radius: 25px 20px 25px 20px; }
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px) saturate(150%) brightness(1.05);
        -webkit-backdrop-filter: blur(20px) saturate(150%) brightness(1.05);
        padding: 16px;
        border-radius: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.6),
                    inset 0 -1px 0 0 rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.5);
        border-left: 5px solid;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: liquidMove 15s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: rotate 40s linear infinite;
        pointer-events: none;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px 0 rgba(31, 38, 135, 0.4),
                    0 0 20px rgba(255, 255, 255, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.8);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.1) 100%);
        border: 2px solid rgba(255, 255, 255, 0.7);
    }
    
    .risk-high {
        color: var(--danger-red);
        font-weight: 700;
        font-size: 15px;
        border-left-color: var(--danger-red);
    }
    
    .risk-medium {
        color: var(--warning-amber);
        font-weight: 700;
        font-size: 15px;
        border-left-color: var(--warning-amber);
    }
    
    .risk-low {
        color: var(--success-green);
        font-weight: 700;
        font-size: 15px;
        border-left-color: var(--success-green);
    }
    
    .opportunity-card {
        border-left-color: var(--accent-teal);
    }
    
    .stMetric {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%) !important;
        backdrop-filter: blur(25px) saturate(150%) brightness(1.1);
        -webkit-backdrop-filter: blur(25px) saturate(150%) brightness(1.1);
        padding: 14px;
        border-radius: 24px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.6),
                    inset 0 -1px 0 0 rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stMetric::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 60%);
        animation: rotate 35s linear infinite reverse;
        pointer-events: none;
    }
    
    .stMetric:hover {
        transform: translateY(-6px) scale(1.03);
        box-shadow: 0 16px 48px 0 rgba(31, 38, 135, 0.4),
                    0 0 25px rgba(255, 255, 255, 0.4),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.8);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0.12) 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.7);
    }
    
    .stMetric label {
        color: white !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        letter-spacing: 0.3px !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 38px !important;
        font-weight: 900 !important;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Main content area buttons - bright and visible */
    .stButton button,
    .main .stButton button,
    [data-testid="stMainBlockContainer"] .stButton button {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: white !important;
        border: 2px solid #fdba74 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4) !important;
        min-height: 48px !important;
    }
    
    .stButton button:hover,
    .main .stButton button:hover,
    [data-testid="stMainBlockContainer"] .stButton button:hover {
        background: linear-gradient(135deg, #fb923c 0%, #f97316 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5) !important;
    }
    
    /* Markdown text visibility in main content */
    .main .stMarkdown,
    .main .stMarkdown p,
    .main .stMarkdown h1,
    .main .stMarkdown h2,
    .main .stMarkdown h3,
    .main .stMarkdown strong,
    [data-testid="stMainBlockContainer"] .stMarkdown {
        color: white !important;
    }
    
    .main hr {
        border-color: rgba(255, 255, 255, 0.3) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(25px) saturate(150%);
        -webkit-backdrop-filter: blur(25px) saturate(150%);
        padding: 12px;
        border-radius: 20px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.5);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        padding: 14px 28px;
        font-weight: 700;
        font-size: 15px;
        color: white;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: transparent;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%) !important;
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        box-shadow: 0 4px 20px 0 rgba(255, 255, 255, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.8) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.6);
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
    }
    
    .stExpander {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
        border-radius: 18px;
        margin-bottom: 8px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.25),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stExpander summary {
        color: white !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stExpander:hover {
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.35),
                    0 0 20px rgba(255, 255, 255, 0.2),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.7);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%);
        transform: translateY(-3px);
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 10px rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 255, 255, 0.3), 0 2px 8px rgba(0, 0, 0, 0.3); }
        50% { text-shadow: 0 0 20px rgba(255, 255, 255, 0.8), 0 0 30px rgba(255, 255, 255, 0.5), 0 2px 8px rgba(0, 0, 0, 0.3); }
    }
    
    .section-header {
        font-size: 26px;
        font-weight: 900;
        color: white;
        margin: 24px 0 18px 0;
        padding-bottom: 16px;
        border-bottom: 3px solid rgba(255, 255, 255, 0.4);
        letter-spacing: -0.3px;
        animation: glow 6s ease-in-out infinite;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
        animation: glassShimmer 5s ease-in-out infinite;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(30, 58, 138, 0.95) 0%, rgba(23, 37, 84, 0.98) 100%);
        backdrop-filter: blur(40px) saturate(180%) brightness(1.1);
        -webkit-backdrop-filter: blur(40px) saturate(180%) brightness(1.1);
        border-right: 2px solid rgba(255, 255, 255, 0.25);
        box-shadow: 4px 0 32px rgba(0, 0, 0, 0.5),
                    inset 1px 0 0 rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 60%);
        animation: rotate 50s linear infinite;
        pointer-events: none;
    }
    
    @media (max-width: 768px) {
        div[data-testid="stSidebar"] {
            width: 100% !important;
        }
    }
    
    div[data-testid="stSidebar"] .element-container {
        color: white;
    }
    
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stMultiSelect label {
        color: white !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.8);
        margin-bottom: 8px !important;
    }
    
    div[data-testid="stSidebar"] .stSelectbox > div > div,
    div[data-testid="stSidebar"] .stMultiSelect > div > div {
        background: linear-gradient(135deg, rgba(30, 35, 45, 0.95) 0%, rgba(25, 30, 40, 0.98) 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        border: 2px solid rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4),
                    0 0 15px rgba(59, 130, 246, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        font-weight: 600 !important;
        backdrop-filter: blur(20px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
        transition: all 0.3s ease !important;
        padding: 8px 12px !important;
    }
    
    div[data-testid="stSidebar"] .stMultiSelect > div > div:hover {
        border-color: rgba(59, 130, 246, 0.8) !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5),
                    0 0 25px rgba(59, 130, 246, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    }
    
    div[data-testid="stSidebar"] input {
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.5);
        font-size: 14px !important;
    }
    
    div[data-testid="stSidebar"] input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stSidebar"] [data-baseweb="select"] {
        background: linear-gradient(135deg, rgba(30, 35, 45, 0.95) 0%, rgba(25, 30, 40, 0.98) 100%) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(20px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
    }
    
    div[data-testid="stSidebar"] [data-baseweb="select"]:hover {
        background: linear-gradient(135deg, rgba(35, 40, 50, 0.98) 0%, rgba(30, 35, 45, 0.98) 100%) !important;
        border-color: rgba(102, 126, 234, 0.8) !important;
    }
    
    div[data-testid="stSidebar"] [data-baseweb="tag"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 8px 16px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.6),
                    0 0 20px rgba(239, 68, 68, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.4) !important;
        transition: all 0.3s ease !important;
        margin: 4px 4px 4px 0 !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    }
    
    div[data-testid="stSidebar"] [data-baseweb="tag"]:hover {
        transform: scale(1.08);
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.8),
                    0 0 30px rgba(239, 68, 68, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%) !important;
    }
    
    div[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 14px 24px !important;
        transition: all 0.3s ease !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.5) !important;
        width: 100% !important;
        min-height: 50px !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    div[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.6) !important;
    }
    
    div[data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4) !important;
    }
    
    @media (max-width: 768px) {
        div[data-testid="stSidebar"] .stButton > button {
            font-size: 14px !important;
            padding: 14px 20px !important;
            min-height: 48px !important;
        }
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 24px;
        font-size: 12px;
        font-weight: 600;
        margin: 4px 0;
        letter-spacing: 0.3px;
    }
    
    .status-active {
        background: var(--success-green);
        color: white;
    }
    
    .status-warning {
        background: var(--warning-amber);
        color: white;
    }
    
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    hr {
        border-color: var(--neutral-200);
    }
    
    .stAlert {
        border-radius: 18px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%);
        backdrop-filter: blur(25px) saturate(150%);
        -webkit-backdrop-filter: blur(25px) saturate(150%);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.6);
        font-weight: 600;
        font-size: 14px;
        color: white;
    }
    
    .element-container {
        color: #1e293b;
    }
    
    p, span, div {
        color: inherit;
    }
    
    .stDataFrame {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        backdrop-filter: blur(25px) saturate(150%);
        -webkit-backdrop-filter: blur(25px) saturate(150%);
        border-radius: 18px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.5);
    }
    
    .stDataFrame table {
        font-size: 14px !important;
        color: white !important;
    }
    
    .stDataFrame thead tr th {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        padding: 14px 12px !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3) !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stDataFrame tbody tr {
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: rgba(255, 255, 255, 0.12) !important;
    }
    
    .stDataFrame tbody tr td {
        color: white !important;
        font-weight: 600 !important;
        padding: 12px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize database and processors
@st.cache_resource(ttl=300)  # Refresh cache every 5 minutes
def init_system():
    db = DatabaseManager()
    processor = DataProcessor(db=db)
    detector = SignalDetector(db=db, processor=processor)
    return db, processor, detector

db, processor, detector = init_system()

# Sidebar
st.sidebar.markdown("""
    <div style="text-align: center; padding: 14px 12px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%); backdrop-filter: blur(25px) saturate(180%); -webkit-backdrop-filter: blur(25px) saturate(180%); border-radius: 24px; margin-bottom: 24px; border: 2px solid rgba(255, 255, 255, 0.25); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), 0 0 20px rgba(102, 126, 234, 0.2), inset 0 2px 0 rgba(255, 255, 255, 0.3);">
        <h2 style="color: white; margin: 0; font-size: 28px; font-weight: 900; text-shadow: 0 3px 12px rgba(0,0,0,0.5), 0 1px 3px rgba(102, 126, 234, 0.5); letter-spacing: -0.5px;">Sri Lanka Business Intelligence</h2>
        <p style="color: rgba(255,255,255,0.95); font-size: 15px; margin-top: 10px; font-weight: 600; text-shadow: 0 2px 6px rgba(0,0,0,0.4);">Real-Time Situational Awareness & Strategic Decision Support</p>
    </div>
""", unsafe_allow_html=True)

# News source filter
st.sidebar.markdown('<p style="color: white; font-weight: 900; font-size: 18px; margin-bottom: 14px; text-shadow: 0 3px 12px rgba(0,0,0,0.9), 0 1px 4px rgba(102, 126, 234, 0.6); letter-spacing: 0.3px;">News Sources</p>', unsafe_allow_html=True)

# Get ENABLED sources from config (only show business-focused sources)
enabled_sources = [config['name'] for key, config in NEWS_SOURCES.items() if config.get('enabled', False)]

# Also get any other sources from database 
db_sources = list(set([src for src in db.get_source_distribution(24*365).keys()]))
all_db_sources = sorted(list(set(enabled_sources + db_sources)))

# Initialize session state - default to ONLY enabled sources
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = sorted(enabled_sources)

# Multi-select for sources
selected_sources = st.sidebar.multiselect(
    "Choose sources to display:",
    options=sorted(all_db_sources),
    default=st.session_state.selected_sources,
    key='source_selector',
    label_visibility="visible"
)

# Update session state
st.session_state.selected_sources = selected_sources

# If nothing selected, show all
if not selected_sources:
    selected_sources = sorted(all_db_sources)

# Show count
st.sidebar.markdown(f'<p style="color: white; font-size: 13px; margin-top: 8px; font-weight: 700; text-shadow: 0 2px 6px rgba(0,0,0,0.8); background: rgba(102, 126, 234, 0.15); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(102, 126, 234, 0.3);">{len(selected_sources)} of {len(all_db_sources)} sources selected</p>', unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin: 8px 0; border-top: 1px solid rgba(255,255,255,0.2);"></div>', unsafe_allow_html=True)

# Time range selector
st.sidebar.markdown('<p style="color: white; font-weight: 900; font-size: 18px; margin-bottom: 14px; text-shadow: 0 2px 8px rgba(0,0,0,0.6), 0 1px 3px rgba(102, 126, 234, 0.4); letter-spacing: 0.3px;">Time Window</p>', unsafe_allow_html=True)
time_range = st.sidebar.selectbox(
    "Time Window",
    [
        "Live – Last 6 Hours",
        "Live – Last 12 Hours",
        "Live – Last 24 Hours",
        "Recent – Last 48 Hours",
        "Recent – Last 72 Hours",
        "Week – Last 7 Days",
        "Biweekly – Last 14 Days",
        "Monthly – Last 30 Days",
    ],
    index=5,
    label_visibility="collapsed",
)

# Professional, non-overlapping windows (older bound, newer bound)
time_map = {
    "Live – Last 6 Hours": (6, 0),
    "Live – Last 12 Hours": (12, 0),
    "Live – Last 24 Hours": (24, 0),
    "Recent – Last 48 Hours": (48, 0),
    "Recent – Last 72 Hours": (72, 0),
    "Week – Last 7 Days": (168, 0),
    "Biweekly – Last 14 Days": (336, 0),
    "Monthly – Last 30 Days": (720, 0),
}
hours_start, hours_end = time_map[time_range]

st.sidebar.markdown('<div style="margin: 10px 0; border-top: 2px solid rgba(102, 126, 234, 0.4); box-shadow: 0 1px 8px rgba(102, 126, 234, 0.3);"></div>', unsafe_allow_html=True)

# Refresh button
if st.sidebar.button("Refresh Data", type="primary", key="refresh_btn"):
    st.cache_data.clear()
    st.rerun()

# Run Collection button - using key for unique identification
if st.sidebar.button("Run Collection", type="primary", key="collection_btn"):
    st.session_state.run_collection = True

# ML Model Controls
if st.sidebar.button("Retrain ML Model", type="primary", key="retrain_btn"):
    st.session_state.retrain_ml = True

# Show ML Model Status
try:
    ml_info = processor.get_ml_info() if hasattr(processor, 'get_ml_info') else {'ml_available': False}
except Exception:
    ml_info = {'ml_available': False}
    
if ml_info.get('ml_available', False):
    ml_status = "Trained" if ml_info.get('is_trained') else "Not Trained"
    ml_accuracy = ml_info.get('accuracy', 0) * 100
    status_color = "#10b981" if ml_info.get('is_trained') else "#f59e0b"
    st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.06) 100%); backdrop-filter: blur(16px); padding: 12px; border-radius: 10px; margin-top: 10px; border: 1px solid rgba(255, 255, 255, 0.2);">
            <p style="color: rgba(255, 255, 255, 0.95); font-size: 13px; margin: 0; font-weight: 500;">
                <strong>ML Model:</strong> <span style="color: {status_color}; font-weight: bold;">{ml_status}</span><br/>
                <strong>Accuracy:</strong> {ml_accuracy:.1f}%
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255, 200, 100, 0.15) 0%, rgba(255, 150, 50, 0.1) 100%); backdrop-filter: blur(16px); padding: 12px; border-radius: 10px; margin-top: 10px; border: 1px solid rgba(255, 200, 100, 0.3);">
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 13px; margin: 0; font-weight: 500;">
                ML: Using keyword fallback
            </p>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin: 10px 0; border-top: 2px solid rgba(102, 126, 234, 0.4); box-shadow: 0 1px 8px rgba(102, 126, 234, 0.3);"></div>', unsafe_allow_html=True)

# Auto-refresh toggle with interval selection and auto-collection
st.sidebar.markdown('<p style="color: white; font-weight: 900; font-size: 18px; margin-bottom: 14px; text-shadow: 0 2px 8px rgba(0,0,0,0.6), 0 1px 3px rgba(102, 126, 234, 0.4); letter-spacing: 0.3px;">Real-Time Updates</p>', unsafe_allow_html=True)

auto_refresh = st.sidebar.checkbox("Enable Auto-refresh", value=False, key="auto_refresh")
auto_collect = st.sidebar.checkbox("Auto-collect new articles", value=False, disabled=not auto_refresh, key="auto_collect", help="Automatically scrape new articles on each refresh")
refresh_interval = st.sidebar.selectbox(
    "Refresh Interval",
    options=["1 minute", "5 minutes", "15 minutes", "30 minutes", "1 hour"],
    index=1,  # Default to 5 minutes
    disabled=not auto_refresh,
    key="refresh_interval"
)

# Convert to milliseconds for st_autorefresh
interval_ms = {
    "1 minute": 60000, 
    "5 minutes": 300000, 
    "15 minutes": 900000,
    "30 minutes": 1800000,
    "1 hour": 3600000
}.get(refresh_interval, 300000)

# Display last updated time and handle auto-collection
last_update_time = datetime.now().strftime('%H:%M:%S')

# Track last collection time in session state
if 'last_collection_time' not in st.session_state:
    st.session_state.last_collection_time = None
if 'collection_count' not in st.session_state:
    st.session_state.collection_count = 0

if auto_refresh:
    # Apply auto-refresh
    refresh_count = st_autorefresh(interval=interval_ms, limit=None, key="data_refresh")
    
    # Auto-collect if enabled and enough time has passed
    if auto_collect:
        should_collect = False
        if st.session_state.last_collection_time is None:
            should_collect = True
        else:
            time_since_last = (datetime.now() - st.session_state.last_collection_time).total_seconds()
            # Only collect if at least the refresh interval has passed
            if time_since_last >= (interval_ms / 1000) - 10:  # 10 second buffer
                should_collect = True
        
        if should_collect:
            # Run background collection
            with st.spinner("Collecting new articles..."):
                try:
                    scraper = NewsScraper()
                    new_articles = scraper.scrape_all()
                    scraper.close()
                    
                    # Process the new articles
                    db_collect = DatabaseManager()
                    proc_collect = DataProcessor(db=db_collect)
                    processed = proc_collect.process_articles()
                    db_collect.close()
                    
                    st.session_state.last_collection_time = datetime.now()
                    st.session_state.collection_count += 1
                    st.cache_data.clear()  # Clear cache to show new data
                except Exception as e:
                    st.sidebar.warning(f"Collection error: {str(e)[:50]}")
    
    # Show live status
    collect_status = ""
    if auto_collect and st.session_state.last_collection_time:
        collect_status = f"<br/><span style='font-size: 11px;'>Collections: {st.session_state.collection_count} | Last: {st.session_state.last_collection_time.strftime('%H:%M:%S')}</span>"
    
    st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0, 255, 100, 0.15) 0%, rgba(0, 200, 80, 0.1) 100%); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(0, 255, 100, 0.3); margin-top: 10px;">
            <p style="color: #00ff88; font-size: 13px; margin: 0; font-weight: 600;">
                <span style="display: inline-block; width: 8px; height: 8px; background: #22c55e; border-radius: 50%; margin-right: 6px; animation: pulse 2s infinite;"></span>LIVE - Refreshing every {refresh_interval}<br/>
                <span style="font-size: 11px; opacity: 0.85;">Last updated: {last_update_time}</span>
                {collect_status}
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.15); margin-top: 10px;">
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 13px; margin: 0; font-weight: 500;">
                Auto-refresh disabled<br/>
                <span style="font-size: 11px; opacity: 0.85;">Last loaded: {last_update_time}</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin: 10px 0; border-top: 2px solid rgba(102, 126, 234, 0.4); box-shadow: 0 1px 8px rgba(102, 126, 234, 0.3);"></div>', unsafe_allow_html=True)

# Show current data stats
st.sidebar.markdown('<p style="color: white; font-weight: 900; font-size: 18px; margin-bottom: 14px; text-shadow: 0 2px 8px rgba(0,0,0,0.6), 0 1px 3px rgba(102, 126, 234, 0.4); letter-spacing: 0.3px;">Quick Stats</p>', unsafe_allow_html=True)
total_articles_db = db.get_total_articles()
st.sidebar.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%); backdrop-filter: blur(20px) saturate(160%); -webkit-backdrop-filter: blur(20px) saturate(160%); padding: 18px; border-radius: 12px; margin-bottom: 14px; border: 1.5px solid rgba(255, 255, 255, 0.25); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 20px rgba(102, 126, 234, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2);">
        <p style="color: rgba(255, 255, 255, 0.96); font-size: 15px; margin: 0; font-weight: 600; line-height: 1.8; text-shadow: 0 1px 4px rgba(0,0,0,0.4);">
            <strong style="font-weight: 700;">Total in DB:</strong> <span style="color: #4facfe; font-weight: 700; text-shadow: 0 0 10px rgba(79, 172, 254, 0.5);">{total_articles_db}</span><br/>
            <strong style="font-weight: 700;">Analyzing:</strong> <span style="color: #f093fb; font-weight: 700; text-shadow: 0 0 10px rgba(240, 147, 251, 0.5);">{time_range}</span><br/>
            <strong style="font-weight: 700;">Sources:</strong> <span style="color: #00f2fe; font-weight: 700; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);">{len(selected_sources)}</span>
        </p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin: 10px 0; border-top: 2px solid rgba(102, 126, 234, 0.4); box-shadow: 0 1px 8px rgba(102, 126, 234, 0.3);"></div>', unsafe_allow_html=True)

st.sidebar.markdown('<p style="color: white; font-weight: 900; font-size: 18px; margin-bottom: 14px; text-shadow: 0 2px 8px rgba(0,0,0,0.6), 0 1px 3px rgba(102, 126, 234, 0.4); letter-spacing: 0.3px;">About</p>', unsafe_allow_html=True)
st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%); backdrop-filter: blur(20px) saturate(160%); -webkit-backdrop-filter: blur(20px) saturate(160%); padding: 18px; border-radius: 12px; color: rgba(255, 255, 255, 0.96); font-size: 15px; line-height: 1.7; border: 1.5px solid rgba(255, 255, 255, 0.25); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 20px rgba(102, 126, 234, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2); font-weight: 600; text-shadow: 0 1px 4px rgba(0,0,0,0.4);">
        Real-time situational awareness platform providing actionable intelligence for Sri Lankan businesses through advanced data analytics.
    </div>
""", unsafe_allow_html=True)

# Main content
st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">Sri Lanka Business Intelligence</h1>
        <p class="hero-subtitle">Real-Time Situational Awareness & Strategic Decision Support</p>
    </div>
""", unsafe_allow_html=True)

# Data Collection Panel - Shows when "Run Collection" is clicked
if st.session_state.get('run_collection', False):
    st.markdown('<div class="section-header">Data Collection Console</div>', unsafe_allow_html=True)
    
    with st.container():
        collection_placeholder = st.empty()
        
        with collection_placeholder.container():
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%); 
                            padding: 20px; border-radius: 16px; font-family: 'Courier New', monospace; 
                            border: 2px solid rgba(102, 126, 234, 0.5); margin-bottom: 20px;">
                    <p style="color: #e2e8f0; margin: 0; font-size: 14px; line-height: 1.6;">
                        <span style="color: #93c5fd;">╔═══════════════════════════════════════════════════════════╗</span><br/>
                        <span style="color: #93c5fd;">║</span>   <strong style="color: #ffffff;">Sri Lanka Business Intelligence Platform</strong>               <span style="color: #93c5fd;">║</span><br/>
                        <span style="color: #93c5fd;">║</span>   Real-Time Situational Awareness System                 <span style="color: #93c5fd;">║</span><br/>
                        <span style="color: #93c5fd;">╚═══════════════════════════════════════════════════════════╝</span><br/><br/>
                        <span style="color: #fbbf24;">Starting collection cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Step 1: Scrape
            with st.spinner("[1/3] Scraping news sources..."):
                scraper = NewsScraper()
                scraped_articles = scraper.scrape_all()
                scraper.close()
            
            st.success(f"✓ Scraped {len(scraped_articles)} articles")
            
            # Show per-source breakdown
            source_counts = {}
            for art in scraped_articles:
                src = art.get('source', 'Unknown')
                source_counts[src] = source_counts.get(src, 0) + 1
            
            if source_counts:
                cols = st.columns(min(len(source_counts), 4))
                for idx, (src, cnt) in enumerate(sorted(source_counts.items())):
                    with cols[idx % 4]:
                        st.metric(src, cnt)
            
            # Step 2: Process
            with st.spinner("[2/3] Processing and categorizing articles..."):
                db_coll = DatabaseManager()
                proc_coll = DataProcessor(db=db_coll)
                processed = proc_coll.process_articles()
            
            st.success(f"✓ Processed {len(processed)} new articles")
            
            # Category distribution
            cat_dist_coll = proc_coll.get_category_distribution(hours_start=24, hours_end=0)
            if cat_dist_coll:
                st.markdown("**Category Distribution (Last 24h):**")
                cat_cols = st.columns(min(len(cat_dist_coll), 5))
                for idx, (cat, cnt) in enumerate(sorted(cat_dist_coll.items(), key=lambda x: x[1], reverse=True)):
                    with cat_cols[idx % 5]:
                        st.metric(cat.title(), cnt)
            
            # Step 3: Signals
            with st.spinner("[3/3] Detecting signals..."):
                det_coll = SignalDetector(db=db_coll, processor=proc_coll)
                signals_coll = det_coll.generate_all_signals()
                det_coll.close()
            
            st.success("✓ Signal detection complete")
            
            # Signal Summary
            st.markdown("---")
            st.markdown("### Signal Summary")
            
            sig_cols = st.columns(4)
            with sig_cols[0]:
                st.metric("Risks", len(signals_coll['risks']))
            with sig_cols[1]:
                st.metric("Opportunities", len(signals_coll['opportunities']))
            with sig_cols[2]:
                st.metric("Trending", len(signals_coll['trending']))
            with sig_cols[3]:
                st.metric("Anomalies", len(signals_coll['anomalies']))
            
            # Top Risks
            if signals_coll['risks']:
                st.markdown("**Top Risks:**")
                for risk in signals_coll['risks'][:3]:
                    severity = risk.get('severity', 'low').upper()
                    color = "#ef4444" if severity == "HIGH" else "#f59e0b" if severity == "MEDIUM" else "#22c55e"
                    st.markdown(f"<span style='color: {color}; font-weight: bold;'>[{severity}]</span> {risk.get('description', '')[:100]}...", unsafe_allow_html=True)
            
            # Top Opportunities
            if signals_coll['opportunities']:
                st.markdown("**Top Opportunities:**")
                for opp in signals_coll['opportunities'][:3]:
                    st.markdown(f"<span style='color: #10b981; font-weight: bold;'>+</span> {opp.get('description', '')[:100]}...", unsafe_allow_html=True)
            
            # Trending
            if signals_coll['trending']:
                st.markdown("**Trending Now:**")
                trend_text = ", ".join([f"**{t['topic']}** ({t['count']})" for t in signals_coll['trending'][:5]])
                st.markdown(trend_text)
            
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%); 
                            padding: 15px; border-radius: 12px; font-family: 'Courier New', monospace; 
                            border: 2px solid rgba(34, 197, 94, 0.5); margin-top: 20px;">
                    <p style="color: #86efac; margin: 0; font-size: 14px;">
                        <span style="color: #93c5fd;">════════════════════════════════════════════════════════════</span><br/>
                        Collection cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
                        <span style="color: #93c5fd;">════════════════════════════════════════════════════════════</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Clear the flag and offer refresh
            if st.button("Refresh Dashboard with New Data"):
                st.session_state.run_collection = False
                st.cache_data.clear()
                st.rerun()
    
    st.markdown("---")

# ML Model Retrain Panel - Shows when "Retrain ML Model" is clicked
if st.session_state.get('retrain_ml', False):
    st.markdown('<div class="section-header">ML Model Training Console</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%); 
                        padding: 20px; border-radius: 16px; font-family: 'Courier New', monospace; 
                        border: 2px solid rgba(147, 51, 234, 0.5); margin-bottom: 20px;">
                <p style="color: #e2e8f0; margin: 0; font-size: 14px; line-height: 1.6;">
                    <span style="color: #c4b5fd;">╔═══════════════════════════════════════════════════════════╗</span><br/>
                    <span style="color: #c4b5fd;">║</span>   <strong style="color: #ffffff;">Machine Learning Model Training</strong>                        <span style="color: #c4b5fd;">║</span><br/>
                    <span style="color: #c4b5fd;">║</span>   TF-IDF + Naive Bayes Classifier                        <span style="color: #c4b5fd;">║</span><br/>
                    <span style="color: #c4b5fd;">╚═══════════════════════════════════════════════════════════╝</span><br/><br/>
                    <span style="color: #fbbf24;">Starting training at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("Training ML model with current database articles..."):
            result = processor.retrain_ml_model()
        
        if result.get('success', False):
            st.success(f"Model trained successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Training Accuracy", f"{result.get('accuracy', 0)*100:.1f}%")
            with col2:
                st.metric("Training Samples", result.get('train_samples', 0))
            with col3:
                st.metric("Categories", result.get('categories', 0))
            
            st.info(f"The ML model uses a hybrid approach: ML predictions are combined with keyword matching for optimal accuracy.")
        else:
            st.error(f"Training failed: {result.get('error', 'Unknown error')}")
            st.warning("Falling back to keyword-based classification")
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%); 
                        padding: 15px; border-radius: 12px; font-family: 'Courier New', monospace; 
                        border: 2px solid rgba(147, 51, 234, 0.5); margin-top: 20px;">
                <p style="color: #86efac; margin: 0; font-size: 14px;">
                    <span style="color: #c4b5fd;">════════════════════════════════════════════════════════════</span><br/>
                    Training completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
                    <span style="color: #c4b5fd;">════════════════════════════════════════════════════════════</span>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Refresh Dashboard"):
            st.session_state.retrain_ml = False
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")

# Get data - Real-time data retrieval (no caching for accuracy)
def get_dashboard_data(hours_start, hours_end, selected_sources_tuple):
    # Convert tuple back to list for filtering
    selected_sources = list(selected_sources_tuple) if selected_sources_tuple else []
    # Pass sources to database for accurate filtering at DB level
    sources_filter = selected_sources if selected_sources else None
    
    # Need to create new DB instance since cached function can't use cached resources
    db_temp = DatabaseManager()
    processor_temp = DataProcessor(db=db_temp)
    # Process any newly scraped but unprocessed articles so categories/sentiments exist
    processor_temp.process_articles()
    
    # Use week-based range query for high accuracy
    articles = db_temp.get_recent_articles(hours=hours_start, hours_end=hours_end, sources=sources_filter)
    
    # Detect signals per source within the same window
    detector_temp = SignalDetector(db=db_temp, processor=processor_temp)
    all_risks = detector_temp.detect_risks(hours_start=hours_start, hours_end=hours_end, sources=sources_filter)
    all_opportunities = detector_temp.detect_opportunities(hours_start=hours_start, hours_end=hours_end, sources=sources_filter)
    
    # Filter risks and opportunities by selected sources
    if sources_filter:
        risks = [r for r in all_risks if r.get('source') in sources_filter]
        opportunities = [o for o in all_opportunities if o.get('source') in sources_filter]
    else:
        risks = all_risks
        opportunities = all_opportunities
    
    # Group by source for per-source analysis
    risks_by_source = {}
    opportunities_by_source = {}
    
    for risk in risks:
        source = risk.get('source', 'Unknown')
        if source not in risks_by_source:
            risks_by_source[source] = []
        risks_by_source[source].append(risk)
    
    for opp in opportunities:
        source = opp.get('source', 'Unknown')
        if source not in opportunities_by_source:
            opportunities_by_source[source] = []
        opportunities_by_source[source].append(opp)
    
    # Get distributions with week-based range for accuracy
    cat_dist = db_temp.get_category_distribution(hours=hours_start, hours_end=hours_end, sources=sources_filter)
    source_dist = db_temp.get_source_distribution(hours=hours_start, hours_end=hours_end, sources=sources_filter)
    
    # Get trending topics for the week
    trending = processor_temp.get_trending_topics(hours_start=hours_start, hours_end=hours_end, sources=sources_filter)
    
    return articles, risks, opportunities, risks_by_source, opportunities_by_source, cat_dist, source_dist, trending

# Initialize articles with empty list as fallback, then populate from function
articles = []
risks = []
opportunities = []
risks_by_source = {}
opportunities_by_source = {}
cat_dist = {}
source_dist = {}
trending = []

articles, risks, opportunities, risks_by_source, opportunities_by_source, cat_dist, source_dist, trending = get_dashboard_data(hours_start, hours_end, tuple(selected_sources))

if not articles:
    st.info(f"No articles found in {time_range}. Try widening the window (e.g., Week – Last 7 Days).")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Articles",
        value=len(articles),
        delta=time_range,
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Risk Signals",
        value=len(risks),
        delta="Active" if risks else "Clear",
        delta_color="inverse" if risks else "normal"
    )

with col3:
    st.metric(
        label="Opportunities",
        value=len(opportunities),
        delta="Identified" if opportunities else "Scanning",
        delta_color="normal"
    )

with col4:
    sources = len(source_dist)
    st.metric(
        label="Active Sources",
        value=sources,
        delta=f"{len(selected_sources)} selected",
        delta_color="off"
    )

st.markdown("---")

# Two column layout
col_left, col_right = st.columns([2, 1])

with col_left:
    # National Activity Indicators
    st.markdown('<div class="section-header">National Activity Indicators</div>', unsafe_allow_html=True)
    
    if cat_dist:
        # Category distribution chart
        df_cat = pd.DataFrame(list(cat_dist.items()), columns=['Category', 'Count'])
        df_cat = df_cat.sort_values('Count', ascending=False)
        
        fig_cat = px.bar(
            df_cat,
            x='Category',
            y='Count',
            title=f'News Coverage by Category ({time_range.split("(")[0].strip()})',
            color='Count',
            color_continuous_scale=['#0891b2', '#2563eb', '#1a365d']
        )
        fig_cat.update_layout(
            showlegend=False,
            height=550,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=13, color='white'),
            title_font_size=18,
            title_font_color='white',
            title_font_weight=700
        )
        fig_cat.update_traces(marker_line_color='rgba(255,255,255,0.4)', marker_line_width=2)
        fig_cat.update_xaxes(tickfont=dict(size=12, color='white'), gridcolor='rgba(255,255,255,0.1)')
        fig_cat.update_yaxes(tickfont=dict(size=12, color='white'), gridcolor='rgba(255,255,255,0.1)')
        st.plotly_chart(fig_cat, width='stretch')
    else:
        st.info("No data available for the selected time range")
    
    # Trending Topics
    st.markdown('<div class="section-header">Trending Topics</div>', unsafe_allow_html=True)
    
    if trending:
        # Create trending topics visualization
        trending_words = [t[0] for t in trending[:10]]
        trending_counts = [t[1] for t in trending[:10]]
        
        df_trending = pd.DataFrame({
            'Topic': trending_words,
            'Mentions': trending_counts
        })
        
        fig_trend = px.bar(
            df_trending,
            x='Mentions',
            y='Topic',
            orientation='h',
            title='Most Mentioned Topics',
            color='Mentions',
            color_continuous_scale=['#059669', '#0891b2', '#2563eb']
        )
        fig_trend.update_layout(
            showlegend=False,
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=13, color='white'),
            title_font_size=18,
            title_font_color='white',
            title_font_weight=700
        )
        fig_trend.update_traces(marker_line_color='rgba(255,255,255,0.4)', marker_line_width=2)
        fig_trend.update_xaxes(tickfont=dict(size=12, color='white'), gridcolor='rgba(255,255,255,0.1)')
        fig_trend.update_yaxes(tickfont=dict(size=12, color='white'))
        st.plotly_chart(fig_trend, width='stretch')
    else:
        st.info("Analyzing trending topics...")
    
    # Source distribution
    if source_dist:
        st.markdown('<div class="section-header">Coverage by Source</div>', unsafe_allow_html=True)
        df_source = pd.DataFrame(list(source_dist.items()), columns=['Source', 'Articles'])
        
        fig_source = px.pie(
            df_source,
            values='Articles',
            names='Source',
            title='Article Distribution by Source',
            color_discrete_sequence=['#2563eb', '#0891b2', '#059669', '#1a365d', '#7c3aed', '#0284c7', '#4f46e5', '#0d9488', '#2dd4bf'],
            hole=0.4
        )
        fig_source.update_layout(
            height=550,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12, color='white'),
            title_font_size=18,
            title_font_color='white',
            title_font_weight=700,
            legend=dict(font=dict(color='white'))
        )
        fig_source.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12, textfont=dict(color='white', family='Inter', weight=700), marker=dict(line=dict(color='rgba(255,255,255,0.3)', width=2)))
        st.plotly_chart(fig_source, width='stretch')

with col_right:
    # Risk & Opportunity Insights
    st.markdown('<div class="section-header">Risk Alerts</div>', unsafe_allow_html=True)
    
    if risks:
        for risk in risks[:5]:
            severity = risk.get('severity', 'low')
            severity_color = "#ef4444" if severity == "high" else "#f59e0b" if severity == "medium" else "#10b981"
            category = risk.get('category', 'General')
            description = risk.get('description', 'No description')
            
            st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
                            padding: 16px 20px; border-radius: 10px; margin-bottom: 12px;
                            border-left: 4px solid {severity_color};">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                        <span style="background: {severity_color}; color: white; padding: 4px 10px; border-radius: 4px;
                                    font-size: 11px; font-weight: 700; text-transform: uppercase;">{severity}</span>
                        <span style="color: rgba(255,255,255,0.7); font-size: 13px;">{category}</span>
                    </div>
                    <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 14px; line-height: 1.5;">{description}</p>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
                        padding: 16px 20px; border-radius: 10px; border-left: 4px solid #10b981;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #10b981; font-weight: 700; font-size: 14px;">ALL CLEAR</span>
                </div>
                <p style="color: rgba(255,255,255,0.7); margin: 8px 0 0 0; font-size: 13px;">No active risk alerts detected</p>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Opportunities
    st.markdown('<div class="section-header">Opportunities</div>', unsafe_allow_html=True)
    
    if opportunities:
        for opp in opportunities[:5]:
            category = opp.get('category', 'General')
            description = opp.get('description', 'No description')
            sentiment = opp.get('sentiment', 0)
            
            st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.05) 100%);
                            padding: 16px 20px; border-radius: 10px; margin-bottom: 12px;
                            border-left: 4px solid #4facfe;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                        <span style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; 
                                    padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">OPPORTUNITY</span>
                        <span style="color: rgba(255,255,255,0.7); font-size: 13px;">{category}</span>
                        <span style="color: #10b981; font-size: 12px; margin-left: auto;">Sentiment: {sentiment:.2f}</span>
                    </div>
                    <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 14px; line-height: 1.5;">{description}</p>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
                        padding: 16px 20px; border-radius: 10px; border-left: 4px solid #6b7280;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: rgba(255,255,255,0.7); font-weight: 600; font-size: 14px;">SCANNING</span>
                </div>
                <p style="color: rgba(255,255,255,0.5); margin: 8px 0 0 0; font-size: 13px;">Monitoring for new opportunities</p>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status
    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
    
    st.markdown(f'''
        <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
                    padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></span>
                    <span style="color: rgba(255,255,255,0.9); font-size: 14px;">Data Collection: <strong style="color: #10b981;">Active</strong></span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></span>
                    <span style="color: rgba(255,255,255,0.9); font-size: 14px;">Signal Detection: <strong style="color: #10b981;">Active</strong></span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></span>
                    <span style="color: rgba(255,255,255,0.9); font-size: 14px;">Analysis Engine: <strong style="color: #10b981;">Running</strong></span>
                </div>
            </div>
            <p style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1); 
                      color: rgba(255,255,255,0.6); font-size: 13px;">
                Last Update: <strong style="color: rgba(255,255,255,0.9);">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>
            </p>
        </div>
    ''', unsafe_allow_html=True)

# Operational Environment Indicators
st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">Operational Environment Intelligence</div>', unsafe_allow_html=True)

# Create tabs for each source plus overview
source_tabs = ["Overview"] + [f"{source}" for source in sorted(selected_sources)]
tabs = st.tabs(source_tabs)

# Overview Tab
with tabs[0]:
    tab1, tab2, tab3 = st.tabs(["Latest News Feed", "Activity Timeline", "Deep Analysis"])
    
    with tab1:
        if articles:
            st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(8, 145, 178, 0.1) 100%); 
                            padding: 16px 24px; border-radius: 12px; margin-bottom: 24px;
                            border-left: 4px solid #2563eb; backdrop-filter: blur(10px);">
                    <p style="color: white; margin: 0; font-size: 15px; font-weight: 600;">
                        Displaying <span style="color: #4facfe; font-weight: 700;">{min(20, len(articles))}</span> of 
                        <span style="color: #4facfe; font-weight: 700;">{len(articles)}</span> articles in selected time range
                    </p>
                </div>
            ''', unsafe_allow_html=True)
            
            # Show recent articles
            for idx, article in enumerate(articles[:20], 1):
                sent_raw = getattr(article, 'sentiment', None)
                sentiment = float(sent_raw) if sent_raw is not None else 0.0
                sentiment_indicator = "positive" if sentiment > 0.2 else "neutral" if sentiment > -0.2 else "negative"
                sentiment_color = "#10b981" if sentiment > 0.2 else "#6b7280" if sentiment > -0.2 else "#ef4444"
                category = str(getattr(article, 'category', None) or 'general')
            
            # Color code by category
            cat_colors = {
                'economy': '#2563eb',
                'politics': '#dc2626',
                'technology': '#059669',
                'business': '#0891b2',
                'general': '#64748b'
            }
            cat_color = cat_colors.get(category, '#757575')
            
            title_str = str(getattr(article, 'title', '') or '')
            url_str = str(getattr(article, 'url', '') or '')
            source_str = str(getattr(article, 'source', '') or '')
            collected_at = getattr(article, 'collected_at', None)
            time_str = collected_at.strftime('%b %d, %Y at %H:%M') if collected_at else ''
            
            # Clean article card without emojis
            st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
                            padding: 20px; border-radius: 12px; margin-bottom: 16px;
                            border: 1px solid rgba(255, 255, 255, 0.15);
                            transition: all 0.3s ease;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div style="flex: 1;">
                            <span style="background: {cat_color}; color: white; padding: 4px 10px; border-radius: 6px; 
                                        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{category}</span>
                            <span style="background: {sentiment_color}; color: white; padding: 4px 10px; border-radius: 6px; 
                                        font-size: 11px; font-weight: 600; margin-left: 8px; text-transform: uppercase;">{sentiment_indicator}</span>
                        </div>
                        <span style="color: rgba(255,255,255,0.5); font-size: 12px;">{time_str}</span>
                    </div>
                    <h4 style="color: white; font-size: 16px; font-weight: 600; margin: 0 0 12px 0; line-height: 1.4;">
                        {idx}. {title_str[:120]}{'...' if len(title_str) > 120 else ''}
                    </h4>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: rgba(255,255,255,0.6); font-size: 13px;">Source: <strong style="color: rgba(255,255,255,0.85);">{source_str}</strong></span>
                        <a href="{url_str}" target="_blank" style="color: #4facfe; font-size: 13px; font-weight: 600; text-decoration: none;
                                  padding: 6px 14px; border: 1px solid #4facfe; border-radius: 6px; transition: all 0.2s ease;"
                           onmouseover="this.style.background='#4facfe'; this.style.color='white';"
                           onmouseout="this.style.background='transparent'; this.style.color='#4facfe';">Read Article →</a>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.info("No articles found in the selected time range. Try expanding the time range or selecting more sources.")

    with tab2:
        if articles:
            # Create timeline
            df_timeline = pd.DataFrame([
                {'time': getattr(a, 'collected_at', None), 'category': str(getattr(a, 'category', None) or 'general')}
                for a in articles
            ])
            
            # Group by hour and category
            df_timeline['hour'] = pd.to_datetime(df_timeline['time']).dt.floor('h')
            timeline_counts = df_timeline.groupby(['hour', 'category']).size().reset_index(name='count')
            
            fig_timeline = px.line(
                timeline_counts,
                x='hour',
                y='count',
                color='category',
                title='Article Activity Over Time',
                labels={'hour': 'Time', 'count': 'Number of Articles', 'category': 'Category'},
                color_discrete_sequence=['#2563eb', '#0891b2', '#059669', '#1a365d', '#7c3aed', '#dc2626']
            )
            fig_timeline.update_layout(
                height=650,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=13, color='white'),
                title_font_size=18,
                title_font_color='white',
                title_font_weight=700,
                hovermode='x unified',
                legend=dict(font=dict(size=12, color='white'), bgcolor='rgba(255,255,255,0.1)', bordercolor='rgba(255,255,255,0.3)', borderwidth=2)
            )
            fig_timeline.update_traces(line_width=4, marker_size=8)
            fig_timeline.update_xaxes(tickfont=dict(size=12, color='white'), gridcolor='rgba(255,255,255,0.1)')
            fig_timeline.update_yaxes(tickfont=dict(size=12, color='white'), gridcolor='rgba(255,255,255,0.1)')
            st.plotly_chart(fig_timeline, width='stretch')
        else:
            st.info("Not enough data for timeline visualization")

    with tab3:
        st.markdown('<p style="color: white; font-size: 20px; font-weight: 800; margin-bottom: 20px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%); padding: 14px 20px; border-radius: 16px; border: 2px solid rgba(255, 255, 255, 0.4); backdrop-filter: blur(20px); box-shadow: 0 4px 20px rgba(31, 38, 135, 0.25), inset 0 1px 0 rgba(255,255,255,0.5); text-shadow: 0 2px 8px rgba(0,0,0,0.3);">Category Breakdown & Sentiment Analysis</p>', unsafe_allow_html=True)
        
        if articles:
            # Create dataframe from articles
            df_proc = pd.DataFrame([{
                'category': str(getattr(a, 'category', None) or 'general'),
                'sentiment': float(getattr(a, 'sentiment', None) or 0),
                'title': str(getattr(a, 'title', '') or '')
            } for a in articles])
            
            # Category sentiment analysis
            cat_sentiment = df_proc.groupby('category').agg({
                'sentiment': 'mean',
                'title': 'count'
            }).reset_index()
            cat_sentiment.columns = ['Category', 'Avg Sentiment', 'Article Count']
            
            fig_sentiment = go.Figure()
            fig_sentiment.add_trace(go.Bar(
                x=cat_sentiment['Category'],
                y=cat_sentiment['Article Count'],
                name='Articles',
                marker_color='rgba(37, 99, 235, 0.8)',
                marker_line_color='rgba(37, 99, 235, 1)',
                marker_line_width=1.5
            ))
            fig_sentiment.add_trace(go.Scatter(
                x=cat_sentiment['Category'],
                y=cat_sentiment['Avg Sentiment'],
                name='Sentiment',
                yaxis='y2',
                marker_color='#059669',
                marker_size=10,
                line=dict(width=3, color='#059669')
            ))
            
            fig_sentiment.update_layout(
                title='Category Analysis: Volume vs Sentiment',
                yaxis=dict(title='Article Count', title_font=dict(color='white', size=14, weight=700), tickfont=dict(size=12, color='white'), gridcolor='rgba(255,255,255,0.1)'),
                yaxis2=dict(title='Avg Sentiment', overlaying='y', side='right', title_font=dict(color='white', size=14, weight=700), tickfont=dict(size=12, color='white')),
                height=650,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=13, color='white'),
                title_font_size=18,
                title_font_color='white',
                title_font_weight=700,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12, color='white'), bgcolor='rgba(255,255,255,0.1)', bordercolor='rgba(255,255,255,0.3)', borderwidth=2)
            )
            
            st.plotly_chart(fig_sentiment, width='stretch')
            
            # Show table with simple styling
            st.markdown('<p style="color: white; font-weight: 800; margin-top: 24px; font-size: 17px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%); padding: 12px 18px; border-radius: 14px; border: 2px solid rgba(255, 255, 255, 0.4); backdrop-filter: blur(20px); box-shadow: 0 4px 20px rgba(31, 38, 135, 0.25), inset 0 1px 0 rgba(255,255,255,0.5); text-shadow: 0 2px 6px rgba(0,0,0,0.3);">Detailed Statistics</p>', unsafe_allow_html=True)
            st.dataframe(
                cat_sentiment,
                hide_index=True
            )
        else:
            st.info("No data available for analysis. Collect more articles to see detailed insights.")

# Per-Source Analysis Tabs
for idx, source in enumerate(sorted(selected_sources), 1):
    with tabs[idx]:
        st.markdown(f'''
            <div style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(8, 145, 178, 0.05) 100%);
                        padding: 20px 24px; border-radius: 12px; margin-bottom: 24px; border-left: 4px solid #2563eb;">
                <h3 style="color: white; margin: 0; font-size: 20px; font-weight: 700;">{source}</h3>
                <p style="color: rgba(255,255,255,0.6); margin: 8px 0 0 0; font-size: 14px;">Intelligence Report & Analysis</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Filter articles for this source
        source_articles = [a for a in articles if str(getattr(a, 'source', '')) == source]
        source_risks = risks_by_source.get(source, [])
        source_opps = opportunities_by_source.get(source, [])
        
        # Source Metrics with cleaner styling
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Articles", len(source_articles))
        with col2:
            st.metric("Risk Alerts", len(source_risks))
        with col3:
            st.metric("Opportunities", len(source_opps))
        
        st.markdown("---")
        
        # Risks for this source
        st.markdown('<div class="section-header">Risk Alerts</div>', unsafe_allow_html=True)
        if source_risks:
            for risk in source_risks[:5]:
                severity = risk.get('severity', 'low')
                severity_color = "#ef4444" if severity == "high" else "#f59e0b" if severity == "medium" else "#10b981"
                description = risk.get('description', 'No description')
                category = risk.get('category', 'General')
                
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
                                padding: 16px 20px; border-radius: 10px; margin-bottom: 12px;
                                border-left: 4px solid {severity_color};">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <span style="background: {severity_color}; color: white; padding: 4px 10px; border-radius: 4px;
                                        font-size: 11px; font-weight: 700; text-transform: uppercase;">{severity}</span>
                            <span style="color: rgba(255,255,255,0.7); font-size: 13px;">{category}</span>
                        </div>
                        <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 14px; line-height: 1.5;">{description}</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.success("No risk alerts from this source")
        
        st.markdown("---")
        
        # Opportunities for this source
        st.markdown('<div class="section-header">Opportunities</div>', unsafe_allow_html=True)
        if source_opps:
            for opp in source_opps[:5]:
                description = opp.get('description', 'No description')
                category = opp.get('category', 'General')
                sentiment = opp.get('sentiment', 0)
                
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.05) 100%);
                                padding: 16px 20px; border-radius: 10px; margin-bottom: 12px;
                                border-left: 4px solid #4facfe;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <span style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; 
                                        padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">OPPORTUNITY</span>
                            <span style="color: rgba(255,255,255,0.7); font-size: 13px;">{category}</span>
                            <span style="color: #10b981; font-size: 12px; margin-left: auto;">Sentiment: {sentiment:.2f}</span>
                        </div>
                        <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 14px; line-height: 1.5;">{description}</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No opportunities identified from this source")
        
        st.markdown("---")
        
        # Recent articles from this source
        st.markdown('<div class="section-header">Recent Articles</div>', unsafe_allow_html=True)
        if source_articles:
            for article in source_articles[:10]:
                sent_raw = getattr(article, 'sentiment', None)
                sentiment = float(sent_raw) if sent_raw is not None else 0.0
                sentiment_color = "#10b981" if sentiment > 0.2 else "#6b7280" if sentiment > -0.2 else "#ef4444"
                category = str(getattr(article, 'category', None) or 'general')
                title_str = str(getattr(article, 'title', '') or '')
                url_str = str(getattr(article, 'url', '') or '')
                collected_at = getattr(article, 'collected_at', None)
                time_str = collected_at.strftime('%b %d, %H:%M') if collected_at else ''
                
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
                                padding: 16px 20px; border-radius: 10px; margin-bottom: 12px;
                                border: 1px solid rgba(255,255,255,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <span style="background: #2563eb; color: white; padding: 3px 10px; border-radius: 4px; 
                                            font-size: 11px; font-weight: 600; text-transform: uppercase;">{category}</span>
                                <span style="color: {sentiment_color}; font-size: 12px; font-weight: 500;">
                                    Sentiment: {sentiment:.2f}</span>
                            </div>
                            <span style="color: rgba(255,255,255,0.5); font-size: 12px;">{time_str}</span>
                        </div>
                        <h4 style="color: white; margin: 0 0 12px 0; font-size: 15px; line-height: 1.4; font-weight: 500;">{title_str}</h4>
                        <a href="{url_str}" target="_blank" style="color: #4facfe; text-decoration: none; font-size: 13px; font-weight: 600;">Read Article &rarr;</a>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info(f"No articles found from {source}")

# Footer
st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
st.markdown(f'''
    <div style="text-align: center; padding: 24px 20px; 
                background: linear-gradient(135deg, rgba(26, 54, 93, 0.9) 0%, rgba(37, 99, 235, 0.8) 100%); 
                border-radius: 16px; margin-top: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.1);">
        <h3 style="color: white; font-size: 18px; font-weight: 700; margin: 0;">
            Sri Lanka Business Intelligence Platform
        </h3>
        <p style="color: rgba(255,255,255,0.8); font-size: 14px; margin: 12px 0 0 0;">
            Real-Time Monitoring & Strategic Insights
        </p>
        <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin-top: 12px;">
            Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
''', unsafe_allow_html=True)
