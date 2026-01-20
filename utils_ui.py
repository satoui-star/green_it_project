"""
LVMH Green in Tech - UI Utilities & Homepage
Light Luxury Theme - Interactive Dashboard
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
# GLOBAL STYLES - RESTORED ORIGINAL FONTS & EXPANDER FIXES
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - restored original font and expander settings"""
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
    
    /* === COMPLETELY HIDE EXPANDER ARROWS (RESTORING ORIGINAL UI) === */
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
    
    /* === RESTORING ORIGINAL TYPOGRAPHY === */
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
    
    /* === ACTION CARDS & BUTTONS === */
    .action-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 40px 30px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 500 !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 6px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-size: 0.75rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# REORGANIZED NARRATIVE COMPONENTS
# =============================================================================

def render_logo():
    """Render the LVMH logo section exactly as your original"""
    st.markdown("""
    <div class="logo-section" style="text-align: center; margin-bottom: 20px; padding: 40px 0 30px 0; border-bottom: 1px solid #e8e4dc;">
        <div style="font-family: 'Playfair Display', serif; font-size: 60px; color: #2c2c2c; letter-spacing: 8px; margin-bottom: 0px;">LVMH</div>
        <div class="logo-tagline" style="font-family: 'Montserrat', sans-serif; font-size: 10px; letter-spacing: 4px; color: #8a6c4a; text-transform: uppercase;">
            Green in Tech Program
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero():
    """Narrative Hero (Static)"""
    st.markdown("""
    <div style="text-align: center; padding: 60px 50px; margin-bottom: 20px;">
        <h1 style="font-size: 3rem !important; margin-bottom: 20px;">Welcome to Green in Tech</h1>
        <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; color: #6a6a6a; max-width: 650px; margin: 0 auto;">
            Our strategic command center for measuring, tracking, and optimizing 
            the environmental impact of LVMH's IT infrastructure across all Maisons.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_program_context():
    """Program Context (Static - No Dynamic Numbers)"""
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin: 30px 0 28px 0; padding-bottom: 15px; border-bottom: 2px solid #e8e4dc;">
        <h2 style="font-size: 1.6rem !important; margin: 0 !important;">Program Context</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #fff; border-left: 3px solid #8a6c4a; border-radius: 0 8px 8px 0; padding: 25px 30px; margin: 18px 0; box-shadow: 0 2px 12px rgba(0,0,0,0.04);">
        <div style="font-family: 'Montserrat', sans-serif; color: #8a6c4a; font-size: 0.7rem; font-weight: 600; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 2px;">LIFE 360 Program</div>
        <p style="font-family: 'Cormorant Garamond', serif; color: #555; line-height: 1.8; font-size: 1.1rem;">
            An alliance of Nature and Creativity. LVMH's LIFE 360 program sets ambitious 
            environmental targets across all Maisons, with Green in Tech focusing on 
            reducing our technological environmental footprint globally.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_pillars():
    """Strategic Pillars (Restored original style)"""
    st.markdown('<h2 style="font-size: 1.6rem; border-bottom: 2px solid #e8e4dc; padding-bottom: 15px;">Strategic Pillars</h2>', unsafe_allow_html=True)
    
    p1, p2, p3, p4 = st.columns(4)
    pillars = [
        ("🔄", "Harmonize", "Unify initiatives across Maisons"),
        ("📊", "Define & Monitor", "Track KPIs at Group level"),
        ("🎛", "Master", "Control environmental impact"),
        ("🚀", "Develop", "Build sustainable IT strategy")
    ]
    
    for col, (icon, title, desc) in zip([p1, p2, p3, p4], pillars):
        with col:
            st.markdown(f"""
            <div style="background: #fff; border: 1px solid #e8e4dc; border-radius: 8px; padding: 28px 22px; text-align: center; height: 100%;">
                <div style="font-size: 1.8rem; margin-bottom: 15px; color: #8a6c4a;">{icon}</div>
                <div style="font-family: 'Montserrat', sans-serif; color: #2c2c2c; font-weight: 600; font-size: 0.75rem; margin-bottom: 10px; text-transform: uppercase;">{title}</div>
                <p style="font-family: 'Cormorant Garamond', serif; color: #777; font-size: 1rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

def render_tools():
    """Navigation to Sub-pages (Cloud & Equipment)"""
    st.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 1.6rem; border-bottom: 2px solid #e8e4dc; padding-bottom: 15px;">Tools</h2>', unsafe_allow_html=True)
    
    nav1, nav2 = st.columns(2)
    
    with nav1:
        st.markdown("""
        <div class="action-card">
            <div style="font-size: 2.5rem; margin-bottom: 20px; color: #8a6c4a;">🖥</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 12px;">Equipment Audit</div>
            <p style="font-family: 'Cormorant Garamond', serif; color: #777; font-size: 1.05rem;">Analyze device lifecycle and get ROI recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Equipment Audit", key="nav_eq", use_container_width=True):
            st.session_state['page'] = 'equipment'
            st.rerun()
            
    with nav2:
        st.markdown("""
        <div class="action-card">
            <div style="font-size: 2.5rem; margin-bottom: 20px; color: #8a6c4a;">☁</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 12px;">Cloud Optimizer</div>
            <p style="font-family: 'Cormorant Garamond', serif; color: #777; font-size: 1.05rem;">Optimize storage and plan archival strategies</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Cloud Optimizer", key="nav_cl", use_container_width=True):
            st.session_state['page'] = 'cloud'
            st.rerun()

def render_insights():
    """Static Strategic Insights (No Buttons)"""
    st.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 1.6rem; border-bottom: 2px solid #e8e4dc; padding-bottom: 15px;">Strategic Insights</h2>', unsafe_allow_html=True)
    
    i1, i2, i3 = st.columns(3)
    
    insights = [
        ("🔋 High Impact", "Server consolidation could reduce energy by 15%"),
        ("⏰ Lifecycle", "234 devices can be extended, saving €450K"),
        ("☁️ Cloud", "Green regions could cut cloud carbon by 30%")
    ]
    
    for col, (title, text) in zip([i1, i2, i3], insights):
        with col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f0f7f1 0%, #fff 100%); border: 1px solid #c8e6c9; border-radius: 8px; padding: 24px; height: 100%;">
                <div style="font-family: 'Montserrat', sans-serif; color: #2e7d32; font-weight: 600; font-size: 0.7rem; margin-bottom: 12px; text-transform: uppercase;">{title}</div>
                <p style="font-family: 'Cormorant Garamond', serif; color: #555; font-size: 1.05rem;">{text}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# MAIN HOMEPAGE FUNCTION
# =============================================================================

def show_home_page():
    """Main function - Narrative Narrative Strategy"""
    inject_global_styles()
    
    render_logo()
    render_hero()
    render_program_context()
    render_pillars()
    render_tools()
    render_insights()
    
    # Footer
    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 30px 0; border-top: 1px solid #e8e4dc;">
        <p style="font-family: 'Montserrat', sans-serif; color: #aaa; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase;">
            LVMH Green in Tech · Alberthon 2025
        </p>
    </div>
    """, unsafe_allow_html=True)
