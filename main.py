import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LVMH • Green IT Cockpit",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# --- LUXURY CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

    /* GENERAL */
    .stApp { background-color: #FAFAFA; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #1E1E1E; }
    
    /* TAGS */
    .lvmh-tag {
        border: 1px solid #D4C5B0; color: #8C8273; padding: 5px 12px;
        border-radius: 4px; font-family: 'Playfair Display', serif; font-size: 14px;
        display: inline-block; background: #FCFBF9; margin-bottom: 15px;
    }

    /* KPI CARDS */
    .kpi-container {
        background-color: white; padding: 24px; border-radius: 8px;
        border: 1px solid #EAEAEA; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        transition: transform 0.2s;
    }
    .kpi-container:hover { transform: translateY(-2px); }
    .kpi-label { font-size: 12px; text-transform: uppercase; color: #666; letter-spacing: 1px; margin-bottom: 8px; }
    .kpi-val { font-size: 32px; font-weight: 700; color: #222; font-family: 'Playfair Display', serif; }
    .badge { font-size: 11px; padding: 4px 10px; border-radius: 12px; font-weight: 600; display: inline-block; margin-top: 5px; }
    .badge-green { background: #E8F5E9; color: #2E7D32; }
    .badge-red { background: #FFEBEE; color: #C62828; }

    /* NAV CARDS */
    .nav-card {
        background: white; border: 1px solid #E0E0E0; border-radius: 10px;
        padding: 30px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
    }
    .nav-title { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; margin-bottom: 10px; color: #4A3B32; }
    .nav-desc { font-size: 14px; color: #666; line-height: 1.6; margin-bottom: 25px; }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #F8F5F2; border-right: 1px solid #EAEAEA; }
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

def navigate_to(page):
    st.session_state.current_page = page

# --- MODULE IMPORTS (Safe Mode) ---
try:
    from equipement_audit import audit_ui
except ImportError:
    audit_ui = None

try:
    from cloud import cloud_ui
except ImportError:
    cloud_ui = None

# --- VIEW: HOME ---
def render_home():
    # Header
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        st.markdown('<div class="lvmh-tag">LVMH</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px; letter-spacing:1px; color:#888; text-transform:uppercase;">Green in Tech • Decision Support Platform</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="font-size: 48px; margin-top: 0;">Sustainable IT Cockpit</h1>', unsafe_allow_html=True)
    
    # KPI Row
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-label">IT Carbon Footprint</div>
            <div class="kpi-val">4,102 tCO₂e</div>
            <div class="badge badge-green">↓ -5% YoY</div>
        </div>""", unsafe_allow_html=True)
        
    with k2:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-label">Active Assets</div>
            <div class="kpi-val">14,205</div>
            <div class="badge badge-red">↑ +12% Growth</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-label">Energy Efficiency</div>
            <div class="kpi-val">85%</div>
            <div class="badge badge-green">↑ +2 pts</div>
        </div>""", unsafe_allow_html=True)

    with k4:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-label">Reconditioning Rate</div>
            <div class="kpi-val">32%</div>
            <div class="badge badge-green">↑ +5% Target</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Navigation Cards
    c_nav1, c_nav2 = st.columns(2)
    
    with c_nav1:
        st.markdown("""
        <div class="nav-card">
            <div>
                <div class="nav-title">💻 Equipment Audit</div>
                <div class="nav-desc">
                    Inventory analysis (CSV) + policy simulations to estimate cost, CO₂ and feasibility.<br>
                    Includes: <b>Lifecycle Analysis</b> & <b>Fleet Simulation</b>.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Equipment Audit →", key="nav_btn_equip", use_container_width=True):
            navigate_to("Equipment Audit")
            st.rerun()

    with c_nav2:
        st.markdown("""
        <div class="nav-card">
            <div>
                <div class="nav-title">☁️ Cloud Analytics</div>
                <div class="nav-desc">
                    Storage decision support: retention scenarios, region optimization and provider comparison.<br>
                    Includes: <b>Archival ROI Calculator</b>.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Cloud Analytics →", key="nav_btn_cloud", use_container_width=True):
            navigate_to("Cloud Analytics")
            st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("In collaboration with Albert School • Mines Paris – PSL")

# --- MAIN APP LOGIC ---
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        # Customizing the look of radio buttons via basic Streamlit API
        selection = st.radio(
            "Go to module:",
            ["Home", "Equipment Audit", "Cloud Analytics"],
            index=["Home", "Equipment Audit", "Cloud Analytics"].index(st.session_state.current_page),
            label_visibility="collapsed"
        )
        
        if selection != st.session_state.current_page:
            st.session_state.current_page = selection
            st.rerun()

        st.markdown("---")
        st.markdown("### Global Settings")
        st.info("ℹ️ **Config:** Using FY2025 Carbon factors.")

    # Routing
    if st.session_state.current_page == "Home":
        render_home()
        
    elif st.session_state.current_page == "Equipment Audit":
        if audit_ui:
            audit_ui.render_audit_section()
        else:
            st.error("⚠️ Module `equipement_audit/audit_ui.py` not found.")
            
    elif st.session_state.current_page == "Cloud Analytics":
        if cloud_ui:
            cloud_ui.render_cloud_section()
        else:
            st.error("⚠️ Module `cloud/cloud_ui.py` not found.")

if __name__ == "__main__":
    main()