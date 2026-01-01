import streamlit as st
import os

def load_lvmh_style():
    """Injects the Luxury Design System CSS."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Inter:wght@300;400;600&display=swap');
        
        :root{
            --bg: #FFFFFF;
            --sidebar-bg: #FFFFFF;
            --text-main: #1A1A1A;
            --text-sidebar: #333333;
            --muted: #666666;
            --border: #E5E5E5;
            --accent: #8a6c4a; /* LVMH Gold */
            --accentSoft: rgba(138,108,74,0.08);
            --accentLine: rgba(138,108,74,0.30);
            --card-bg: #FAFAFA;
            --negative: #A65D57;
        }

        /* --- MAIN CONTAINER --- */
        .stApp{ background-color: var(--bg); color: var(--text-main); }
        header[data-testid="stHeader"] { background-color: transparent !important; }
        section[data-testid="stMain"]{ padding-top: 1.0rem; }

        /* Typography */
        h1,h2,h3,h4,h5{ font-family:'Playfair Display',serif!important; color: #000000 !important; letter-spacing: 0.5px; }
        p,div,label,li,.stMarkdown{ font-family:'Inter',sans-serif; font-weight: 300; line-height: 1.65; color: var(--text-main); }
        .small-muted{ color:var(--muted); font-size:0.95rem; }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"]{ background-color: var(--sidebar-bg); border-right: 1px solid #E5E5E5; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: var(--accent) !important; }
        
        /* --- CARDS & HERO --- */
        .hero{
            background: linear-gradient(135deg, #F8F5F2, #FFFFFF);
            border: 1px solid var(--accentLine);
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        }
        .hero-title{ font-size: 2.65rem; margin: 0; color: #000; font-family:'Playfair Display',serif; }
        .hero-sub{ margin-top: 10px; color: var(--muted); letter-spacing: 2.4px; text-transform: uppercase; font-size: .82rem; }
        .hero-row{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
        .chip{ border: 1px solid var(--accentLine); background: #FFFFFF; color: #555; padding: 6px 12px; border-radius: 999px; font-size: .80rem; font-weight: 500; }

        .card{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            height: 100%;
            transition: all .2s ease;
        }
        .card:hover{ border-color: var(--accent); box-shadow: 0 8px 24px rgba(138,108,74,0.15); transform: translateY(-2px); }
        .card-title{ display:flex; align-items:center; gap:10px; color: var(--accent); font-family:'Playfair Display',serif; font-size: 1.18rem; margin-bottom: 10px; font-weight: 600; }
        .divider{ height:1px; background: linear-gradient(90deg, #E0E0E0, transparent); margin: 10px 0 12px 0; }
        
        /* Metrics */
        div[data-testid="stMetric"]{ background: #FFFFFF; border: 1px solid var(--border); border-left: 3px solid var(--accent); padding: 12px 14px; border-radius: 10px; }
        div[data-testid="stMetricValue"]{ font-family:'Playfair Display',serif!important; font-size: 1.55rem !important; }
        
        /* Buttons */
        .stButton > button{ background: #FFFFFF; border: 1px solid var(--accent); color: var(--accent); border-radius: 8px; padding: 0.58rem 0.92rem; font-weight: 500; transition: 0.3s; }
        .stButton > button:hover{ background: var(--accent); color: #FFFFFF; border-color: var(--accent); }
        
        /* Navigation Hiding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Header Components */
        .topline{ height: 1px; background: linear-gradient(90deg, var(--accent), transparent); margin: 12px 0 18px 0; }
        .header-title{ font-family:'Playfair Display',serif; color: #000; font-size: 1.02rem; font-weight: 600; }
        .header-sub{ color: var(--muted); font-size: 0.82rem; letter-spacing: 2.2px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renders the standard LVMH Header."""
    left, center, right = st.columns([1.6, 6, 1.0], gap="large")
    with left:
        st.markdown("""
        <div style="display:inline-block; padding:10px 18px; border-radius:12px; background: #F8F5F2; border:1px solid rgba(138,108,74,0.3);">
            <div style='font-family:Playfair Display,serif;color:#8a6c4a;letter-spacing:1px;font-size:1.35rem;'>LVMH</div>
        </div>
        """, unsafe_allow_html=True)
    with center:
        st.markdown("<div class='header-title'>Green in Tech • Decision Support Platform</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-sub'>Equipment & Cloud Storage</div>", unsafe_allow_html=True)
    with right:
        st.write("")
        st.markdown("<div class='topline'></div>", unsafe_allow_html=True)

def render_assumptions_drawer():
    """Renders the right-hand assumption column."""
    st.markdown("### Assumptions")
    st.caption("Transparent, configurable inputs to make ROI defensible (consulting-grade).")
    with st.expander("Open assumptions (Methodology)", expanded=False):
        st.markdown("#### Global Settings")
        st.number_input("Carbon Intensity (kgCO2e/kWh)", value=0.06, step=0.01)
        st.number_input("Cloud Energy (kWh/GB-mo)", value=0.002, format="%.4f")