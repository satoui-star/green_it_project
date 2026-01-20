import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

def inject_global_styles():
    """Master CSS - NEVER CHANGE THIS FUNCTION NAME"""
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
        border-left: 10px solid #DC2626; /* Thick left border */
        border-radius: 12px;
        padding: 30px;
        margin: 35px 0;
        display: flex;
        align-items: center;
        gap: 25px;
        box-shadow: 0 10px 25px rgba(220, 38, 38, 0.08);
    }
    .action-box-icon {
        font-size: 40px;
        color: #DC2626;
        flex-shrink: 0;
    }
    .action-box-title {
        color: #991B1B !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }
    .action-box-text {
        color: #7F1D1D !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.3rem !important;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

def render_logo():
    logo_path = "logo.png/elysia_logo.png" 
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align:center;padding:30px;"><img src="data:image/png;base64,{encoded}" style="width:280px;"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="text-align:center;letter-spacing:10px;color:#C5A059;">ÉLYSIA</h1>', unsafe_allow_html=True)

def render_footer():
    st.markdown('<div style="text-align:center;margin-top:50px;padding:20px;border-top:1px solid #e8e4dc;"><p style="font-size:0.7rem;letter-spacing:3px;color:#aaa;">ÉLYSIA · ALBERTHON 2026</p></div>', unsafe_allow_html=True)

def show_home_page():
    """NEVER CHANGE THIS FUNCTION NAME"""
    inject_global_styles()
    render_logo()
    st.write("Home content here...")
    render_footer()
