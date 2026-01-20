import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# =============================================================================
# GLOBAL STYLES - KEPT EXACTLY AS YOUR ORIGINAL
# =============================================================================

def inject_global_styles():
    """Master CSS - DO NOT CHANGE THIS FUNCTION NAME"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    .stApp { background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TYPOGRAPHY */
    h1 { font-family: 'Playfair Display', serif !important; color: #2c2c2c !important; }
    h2, h3, h4 { font-family: 'Cormorant Garamond', serif !important; color: #8a6c4a !important; }
    p, span, div, label, li { font-family: 'Montserrat', sans-serif !important; color: #4a4a4a !important; }

    /* CARDS & EXPANDERS */
    [data-testid="stExpander"] { background: #fff !important; border: 1px solid #e8e4dc !important; border-radius: 6px !important; }
    .kpi-card { background: #fff; border: 1px solid #e8e4dc; border-radius: 10px; padding: 30px; text-align: center; margin-bottom: 15px; }

    /* === ENHANCED RED ACTION BOX DESIGN === */
    .action-box-red {
        background-color: #FEF2F2;
        border: 1px solid #F87171;
        border-left: 10px solid #DC2626; 
        border-radius: 12px;
        padding: 30px;
        margin: 35px 0;
        display: flex;
        align-items: center;
        gap: 25px;
        box-shadow: 0 10px 25px rgba(220, 38, 38, 0.08);
    }
    .action-box-icon { font-size: 40px; color: #DC2626; flex-shrink: 0; }
    .action-box-title { color: #991B1B !important; font-family: 'Montserrat', sans-serif !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 5px; }
    .action-box-text { color: #7F1D1D !important; font-family: 'Cormorant Garamond', serif !important; font-size: 1.3rem !important; margin: 0; line-height: 1.4; }

    .gold-divider { height: 1px; background: linear-gradient(90deg, transparent, #d4cfc5, transparent); margin: 50px 0; }
    
    .action-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 40px 30px;
        text-align: center;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# BRANDING & NARRATIVE COMPONENTS
# =============================================================================

def render_logo():
    """Renders the logo from elysia_logo.png in the logo.png folder"""
    logo_path = "logo.png/elysia_logo.png" 
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="text-align: center; padding: 40px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 35px;">
            <img src="data:image/png;base64,{encoded}" style="width: 280px;">
            <div style="font-family: 'Montserrat', sans-serif; font-size: 0.7rem; letter-spacing: 4px; color: #8a6c4a; text-transform: uppercase; margin-top: 10px;">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="text-align:center; color:#C5A059; letter-spacing:8px;">ÉLYSIA</h1>', unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="gold-divider"></div>
    <div style="text-align: center; padding-bottom: 40px;">
        <p style="font-family: 'Montserrat', sans-serif; color: #aaa; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase;">
            Élysia · Alberthon 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN HOMEPAGE FUNCTION - KEPT FOR MAIN.PY IMPORT
# =============================================================================

def show_home_page():
    """Main homepage entry point - NEVER CHANGE THIS NAME"""
    inject_global_styles()
    render_logo()
    
    # Hero Section
    st.markdown("""
    <div style="background: white; border: 1px solid #e8e4dc; border-radius: 8px; padding: 60px; text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 3rem !important; margin-bottom: 20px;">Welcome to Élysia</h1>
        <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; color: #6a6a6a; max-width: 750px; margin: 0 auto; text-align: center;">
            Your strategic command center for measuring, tracking, and optimizing 
            the environmental impact of LVMH's IT infrastructure across all Maisons.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Narrative Context
    st.markdown('### Program Context', unsafe_allow_html=True)
    st.markdown("""
    <div style="background: #fff; border-left: 4px solid #8a6c4a; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.04);">
        <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem;">
            An alliance of Nature and Creativity. LVMH's LIFE 360 program sets ambitious environmental targets across all Maisons, 
            with <strong>Élysia</strong> focusing on reducing the technological environmental footprint.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Section
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown('### Strategic Tools', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="action-card">🖥 <h4>Equipment Audit</h4><p>Analyze device lifecycle and ROI.</p></div>', unsafe_allow_html=True)
        if st.button("Launch Equipment Audit", key="btn_eq"):
            st.session_state['page'] = 'equipment'
            st.rerun()
    with col2:
        st.markdown('<div class="action-card">☁ <h4>Cloud Optimizer</h4><p>Strategic archival and storage optimization.</p></div>', unsafe_allow_html=True)
        if st.button("Launch Cloud Optimizer", key="btn_cl"):
            st.session_state['page'] = 'cloud'
            st.rerun()

    render_footer()
