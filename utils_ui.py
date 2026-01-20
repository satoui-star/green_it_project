"""
LVMH Green in Tech - UI Utilities & Homepage
Light Luxury Theme - Narrative Homepage & Shared Styles
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
import os
import base64

# =============================================================================
# GLOBAL STYLES - FULLY RESTORED FOR COMPATIBILITY
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - Full CSS restoration for Cloud/Equipment pages"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* === LIGHT LUXURY BASE === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === COMPLETELY HIDE EXPANDER ARROWS === */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    [data-testid="stExpander"] svg,
    [data-testid="stExpander"] path,
    .streamlit-expanderHeader svg {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    /* Force hide the icon container */
    [data-testid="stExpander"] summary > span:first-child,
    [data-testid="stExpander"] details > summary > div:first-child {
        display: none !important;
    }
    
    details summary {
        list-style: none !important;
        list-style-type: none !important;
    }
    
    details summary::-webkit-details-marker,
    details summary::marker {
        display: none !important;
        content: "" !important;
        font-size: 0 !important;
    }
    
    /* Style expander container */
    [data-testid="stExpander"] {
        background: #fff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    
    [data-testid="stExpander"] > details > summary {
        padding: 14px 18px !important;
        color: #8a6c4a !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    
    [data-testid="stExpander"] > details > summary:hover {
        color: #6d553a !important;
        background: #faf8f5 !important;
    }
    
    [data-testid="stExpander"] > details[open] > summary {
        border-bottom: 1px solid #e8e4dc !important;
    }
    
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #fdfcfa !important;
        padding: 18px !important;
    }
    
    /* === TYPOGRAPHY === */
    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        font-weight: 500 !important;
        letter-spacing: 2px !important;
    }
    
    h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #8a6c4a !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
    }
    
    p, span, div, label, li {
        font-family: 'Montserrat', sans-serif !important;
        color: #4a4a4a !important;
    }
    
    /* === LOGO SECTION === */
    .logo-section {
        text-align: center;
        padding: 40px 0 30px 0;
        border-bottom: 1px solid #e8e4dc;
        margin-bottom: 35px;
        background: linear-gradient(180deg, #fff 0%, #faf9f7 100%);
    }
    
    .logo-text {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #2c2c2c;
        letter-spacing: 12px;
        font-weight: 400;
        margin-bottom: 12px;
    }
    
    .logo-tagline {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 4px;
        color: #8a6c4a;
        text-transform: uppercase;
    }
    
    /* === WELCOME HERO === */
    .welcome-hero {
        background: linear-gradient(135deg, #fff 0%, #f8f6f2 50%, #fff 100%);
        border: 1px solid #e8e4dc;
        border-radius: 8px;
        padding: 60px 50px;
        margin: 25px 0 45px 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(138, 108, 74, 0.06);
    }
    
    .welcome-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 3rem !important;
        color: #2c2c2c !important;
        margin-bottom: 20px !important;
        line-height: 1.3 !important;
        font-weight: 500 !important;
        letter-spacing: 2px !important;
    }
    
    .welcome-subtitle {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.3rem;
        color: #6a6a6a;
        line-height: 1.8;
        max-width: 650px;
        margin: 0 auto;
        font-weight: 400;
    }
    
    .welcome-date {
        font-family: 'Montserrat', sans-serif;
        color: #999;
        font-size: 0.7rem;
        margin-top: 30px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* === CONTEXT SECTION === */
    .context-card {
        background: #fff;
        border-left: 3px solid #8a6c4a;
        border-radius: 0 8px 8px 0;
        padding: 25px 30px;
        margin: 18px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    
    .context-title {
        font-family: 'Montserrat', sans-serif;
        color: #8a6c4a;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .context-text {
        font-family: 'Cormorant Garamond', serif;
        color: #555;
        line-height: 1.8;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* === KPI CARDS - PROMINENT (NEEDED FOR CLOUD UI) === */
    .kpi-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .kpi-card:hover {
        box-shadow: 0 8px 30px rgba(138, 108, 74, 0.12);
        transform: translateY(-3px);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 3px 3px;
    }
    
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 12px;
        color: #8a6c4a;
    }
    
    .kpi-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.65rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
        font-weight: 500;
    }
    
    .kpi-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.8rem;
        font-weight: 500;
        color: #2c2c2c;
        line
