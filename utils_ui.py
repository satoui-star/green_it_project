"""
LVMH Green in Tech - UI Utilities & Master Styles
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

def inject_global_styles():
    """Master CSS for the entire app. Call this on every page."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TYPOGRAPHY */
    h1 { font-family: 'Playfair Display', serif !important; color: #2c2c2c !important; letter-spacing: 2px !important; }
    h2, h3, h4 { font-family: 'Cormorant Garamond', serif !important; color: #8a6c4a !important; letter-spacing: 1px !important; }
    p, span, div, label, li { font-family: 'Montserrat', sans-serif !important; color: #4a4a4a !important; }

    /* LOGO & HERO */
    .logo-section { text-align: center; padding: 40px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 35px; }
    .welcome-hero { border: 1px solid #e8e4dc; border-radius: 8px; padding: 60px; text-align: center; margin-bottom: 40px; background: white; }

    /* CARDS */
    .kpi-card { background: #fff; border: 1px solid #e8e4dc; border-radius: 10px; padding: 30px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.03); height: 100%; }
    .kpi-value { font-family: 'Playfair Display', serif !important; font-size: 2.5rem; color: #2c2c2c; }
    .context-card { background: #fff; border-left: 4px solid #8a6c4a; padding: 25px; margin: 15px 0; border-radius: 0 8px 8px 0; }

    /* === ENHANCED RED ACTION BOX DESIGN === */
    .action-box-red {
        background-color: #FFF5F5;
        border: 1px solid #FED7D7;
        border-left: 6px solid #E53E3E;
        border-radius: 12px;
        padding: 30px;
        margin: 40px 0;
        box-shadow: 0 10px 25px rgba(229, 62, 62, 0.08);
        display: flex;
        align-items: center;
        gap: 25px;
    }
    .action-box-icon {
        font-size: 35px;
        background: #E53E3E;
        color: white;
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(229, 62, 62, 0.2);
    }
    .action-box-title {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        color: #C53030 !important;
        margin-bottom: 8px !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .action-box-desc {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.3rem !important;
        color: #742A2A !important;
        margin: 0 !important;
        line-height: 1.4 !important;
    }

    /* UTILS */
    .gold-divider { height: 1px; background: linear-gradient(90deg, transparent, #d4cfc5, transparent); margin: 50px 0; }
    .stButton > button { background: #8a6c4a !important; color: white !important; border-radius: 4px !important; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

def render_logo():
    """Consistent Header with Logo"""
    logo_path = "logo/elysia_logo.png" # Standard folder name
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""<div class="logo-section"><img src="data:image/png;base64,{encoded}" style="width: 250px;"><div class="logo-tagline">Where insight drives impact</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="logo-section"><div style="font-family:'Playfair Display';font-size:50px;letter-spacing:8px;color:#C5A059;">ELYSIA</div><div class="logo-tagline">Where insight drives impact</div></div>""", unsafe_allow_html=True)

def render_footer():
    """Consistent Footer"""
    st.markdown("""<div class="gold-divider"></div><div style="text-align:center;padding-bottom:40px;"><p style="font-size:0.7rem;letter-spacing:3px;color:#aaa;">ÉLYSIA · ALBERTHON 2026</p></div>""", unsafe_allow_html=True)
