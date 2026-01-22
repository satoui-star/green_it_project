"""
LVMH Green in Tech - UI Utilities & Homepage
Light Luxury Theme - Fully Centered with Framed Rectangles
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import base64

# =============================================================================
# GLOBAL STYLES - FULL CENTERING & LUXURY FRAMING
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - Centered Layout with Frame Rectangles"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* === BASE APP & GLOBAL CENTERING === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
        text-align: center !important;
    }
    
    p, span, div, label, li {
        text-align: center !important;
        font-family: 'Montserrat', sans-serif !important;
        color: #4a4a4a !important;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* === TYPOGRAPHY CENTERING === */
    h1, h2, h3, h4, .section-title {
        text-align: center !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        letter-spacing: 2px !important;
    }
    
    h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #8a6c4a !important;
        letter-spacing: 1px !important;
    }

    /* === BEAUTIFUL FRAMING BOXES (RECTANGLES) === */
    .pillar-card, .action-card, .context-card, .insight-card, .data-input-section, .chart-container {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 12px !important;
        padding: 30px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 12px rgba(138, 108, 74, 0.04) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }

    .pillar-card:hover, .action-card:hover {
        border-color: #8a6c4a !important;
        box-shadow: 0 8px 24px rgba(138, 108, 74, 0.12) !important;
        transform: translateY(-2px);
    }

    /* Context Card specific framing */
    .context-card {
        border-left: 4px solid #8a6c4a !important;
        border-radius: 4px 12px 12px 4px !important;
    }

    /* === KPI CARDS === */
    .kpi-card {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 12px !important;
        padding: 40px 25px !important;
        text-align: center !important;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06) !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 60px; height: 4px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 4px 4px;
    }

    .kpi-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.8rem;
        color: #2c2c2c !important;
    }

    /* === URGENT ALERT (RED BOX) CENTERING === */
    div.urgent-alert {
        background: #fef2f2 !important;
        padding: 35px !important;
        border-radius: 12px !important;
        border: 2px solid #ef4444 !important; 
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.1) !important;
        margin: 30px 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
    }

    div.urgent-alert-header {
        color: #991b1b !important;
        margin-bottom: 15px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.9rem !important;
        justify-content: center !important;
    }

    /* === BUTTONS === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        border-radius: 8px !important;
        padding: 12px 30px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* === EXPANDERS === */
    [data-testid="stExpander"] {
        background: #fff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 6px !important;
    }
    [data-testid="stExpander"] svg { display: none !important; }

    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# REORGANIZED NARRATIVE COMPONENTS
# =============================================================================

def render_logo():
    """Render a significantly larger Elysia logo, centered and positioned high."""
    logo_path = "logo.png/elysia_logo.png" 

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        st.markdown(f"""
        <div class="logo-section" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px 0 20px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 35px; background: white;">
            <img src="data:image/png;base64,{encoded}" alt="Elysia Logo" style="width: 450px; max-width: 95%; margin-bottom: 5px; display: block; margin: 0 auto;">
            <div style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; letter-spacing: 5px; color: #8a6c4a; text-transform: uppercase; margin-top: -5px; text-align: center;">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="logo-section" style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 35px; background: white;">
            <div style="font-family: 'Playfair Display', serif; font-size: 80px; color: #8a6c4a; letter-spacing: 15px; line-height: 1; text-align: center;">ELYSIA</div>
            <div style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; letter-spacing: 5px; color: #8a6c4a; text-transform: uppercase; margin-top: 10px; text-align: center;">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_welcome_section():
    """Centered Hero section."""
    st.markdown(f"""
    <div class="welcome-hero" style="text-align: center; margin-bottom: 50px;">
        <h1 style="font-size: 3.5rem !important; margin-bottom: 15px !important; text-align: center;">Welcome to Élysia</h1>
        <p style="text-align: center; margin: 0 auto; max-width: 850px; font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; color: #6a6a6a; line-height: 1.6;">
            Your strategic command center for measuring, tracking, and optimizing 
            the environmental impact of LVMH's IT infrastructure across all Maisons.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_urgent_alert(header_text, title_text, paragraph_text):
    """Specific function to render the Urgent Red Box with full centering."""
    st.markdown(f"""
    <div class="urgent-alert">
        <div class="urgent-alert-header">🚨 {header_text}</div>
        <h3 style="text-align: center;">{title_text}</h3>
        <p style="text-align: center;">{paragraph_text}</p>
    </div>
    """, unsafe_allow_html=True)

# Ensure the rest of your page functions (render_context_section, render_pillars_section, etc.) 
# call the inject_global_styles() function at the start to apply these alignments.
