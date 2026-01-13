import streamlit as st

def load_lvmh_style():
    """Injects the Luxury Design System CSS."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Inter:wght@300;400;600&display=swap');
        
        :root{
            --bg: #FFFFFF; --text-main: #1A1A1A; --muted: #666666;
            --border: #E5E5E5; --accent: #8a6c4a; /* LVMH Gold */
            --card-bg: #FAFAFA;
        }

        .stApp{ background-color: var(--bg); color: var(--text-main); font-family:'Inter',sans-serif; }
        h1,h2,h3{ font-family:'Playfair Display',serif!important; color: #000 !important; }
        
        /* HERO & CARDS */
        .hero{
            background: linear-gradient(135deg, #F8F5F2, #FFFFFF);
            border: 1px solid rgba(138,108,74,0.3); padding: 24px; border-radius: 12px; margin-bottom: 20px;
        }
        .hero-title{ font-size: 2.5rem; font-family:'Playfair Display',serif; color: #000; margin:0; }
        .hero-sub{ color: var(--muted); letter-spacing: 2px; text-transform: uppercase; font-size: 0.8rem; }
        
        .card{
            background: var(--card-bg); border: 1px solid var(--border);
            padding: 20px; border-radius: 10px; height: 100%;
        }
        .card-title{ color: var(--accent); font-family:'Playfair Display',serif; font-size: 1.2rem; font-weight:600; margin-bottom:10px;}

        /* METRICS & TABS */
        div[data-testid="stMetric"]{ background: white; border: 1px solid #eee; border-left: 3px solid var(--accent); padding: 10px; border-radius: 8px; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 4px; border: 1px solid #eee; }
        .stTabs [aria-selected="true"] { background-color: var(--accent) !important; color: white !important; }
        
        /* HEADER */
        .header-title{ font-family:'Playfair Display',serif; font-weight:600; font-size:1.1rem; }
        .topline{ height: 1px; background: linear-gradient(90deg, var(--accent), transparent); margin: 10px 0 20px 0; }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renders the standard header."""
    l, c, r = st.columns([1, 6, 1])
    with l: st.markdown("<div style='color:#8a6c4a;font-family:Playfair Display;font-size:1.2rem;border:1px solid #ddd;padding:5px 10px;border-radius:8px;text-align:center;'>LVMH</div>", unsafe_allow_html=True)
    with c: 
        st.markdown("<div class='header-title'>Green IT • Decision Platform</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#666;font-size:0.8rem;letter-spacing:1px;'>EQUIPMENT & CLOUD</div>", unsafe_allow_html=True)
    with r: st.write("")
    st.markdown("<div class='topline'></div>", unsafe_allow_html=True)