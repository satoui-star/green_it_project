import streamlit as st
import os
import sys

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LVMH Sustainable IT",
    page_icon="⚜️",
    layout="wide"
)

# --- 2. LUXURY DESIGN SYSTEM (White Main + Black Sidebar + Transparent Header) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Inter:wght@300;400;600&display=swap');

    :root{
        --bg: #FFFFFF;
        --sidebar-bg: #0A0A0A;
        --text-main: #1A1A1A;
        --text-sidebar: #E0E0E0;
        --muted: #666666;
        --border: #E5E5E5;
        --accent: #8a6c4a; /* LVMH Gold */
        --accentSoft: rgba(138,108,74,0.08);
        --accentLine: rgba(138,108,74,0.30);
        --card-bg: #FAFAFA;
    }

    /* --- MAIN CONTAINER --- */
    .stApp{
        background-color: var(--bg);
        color: var(--text-main);
    }
    
    /* FIX: Make the top header transparent to remove the white bar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    section[data-testid="stMain"]{ padding-top: 1.0rem; }

    /* Typography */
    h1,h2,h3,h4,h5{
        font-family:'Playfair Display',serif!important;
        color: #000000 !important;
        letter-spacing: 0.5px;
    }
    p,div,label,li,.stMarkdown{
        font-family:'Inter',sans-serif;
        font-weight: 300;
        line-height: 1.65;
        color: var(--text-main);
    }
    .small-muted{ color:var(--muted); font-size:0.95rem; }

    /* --- SIDEBAR (BLACK) --- */
    [data-testid="stSidebar"]{
        background-color: var(--sidebar-bg);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Sidebar Text Coloring */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--accent) !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label {
        color: var(--text-sidebar) !important;
    }
    /* Fix Input/Selectbox labels in sidebar */
    [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stNumberInput label {
        color: var(--text-sidebar) !important;
    }
    
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }

    /* --- COMPONENTS --- */
    .topline{
        height: 1px;
        background: linear-gradient(90deg, var(--accent), transparent);
        margin: 12px 0 18px 0;
    }
    .header-title{
        font-family:'Playfair Display',serif;
        color: #000;
        font-size: 1.02rem;
        text-align:center;
        margin-top: 2px;
        font-weight: 600;
    }
    .header-sub{
        color: var(--muted);
        font-size: 0.82rem;
        letter-spacing: 2.2px;
        text-transform: uppercase;
        text-align:center;
        margin-top: 2px;
    }

    /* Hero Section */
    .hero{
        background: linear-gradient(135deg, #F8F5F2, #FFFFFF);
        border: 1px solid var(--accentLine);
        border-radius: 12px;
        padding: 28px 28px 20px 28px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    .hero-title{ font-size: 2.65rem; margin: 0; color: #000; font-family:'Playfair Display',serif; }
    .hero-sub{
        margin-top: 10px;
        color: var(--muted);
        letter-spacing: 2.4px;
        text-transform: uppercase;
        font-size: .82rem;
    }
    .hero-row{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
    .chip{
        border: 1px solid var(--accentLine);
        background: #FFFFFF;
        color: #555;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: .80rem;
        font-weight: 500;
    }

    /* Cards */
    .card{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        transition: all .2s ease;
    }
    .card:hover{
        border-color: var(--accent);
        box-shadow: 0 8px 24px rgba(138,108,74,0.15);
        transform: translateY(-2px);
    }
    .card-title{
        display:flex; align-items:center; gap:10px;
        color: var(--accent);
        font-family:'Playfair Display',serif;
        font-size: 1.18rem;
        margin: 0 0 10px 0;
        font-weight: 600;
    }
    .divider{
        height:1px;
        background: linear-gradient(90deg, #E0E0E0, transparent);
        margin: 10px 0 12px 0;
    }
    .card-meta{ color: var(--muted); font-size: .9rem; margin: 0; }

    /* Metrics (KPIs) */
    div[data-testid="stMetric"]{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        padding: 12px 14px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"]{ color: var(--muted)!important; font-size: 0.84rem; }
    div[data-testid="stMetricValue"]{
        color: #000!important; 
        font-family:'Playfair Display',serif!important;
        font-size: 1.55rem !important;
        white-space: nowrap;
    }

    /* Buttons */
    .stButton > button{
        background: #FFFFFF;
        border: 1px solid var(--accent);
        color: var(--accent);
        border-radius: 8px;
        padding: 0.58rem 0.92rem;
        font-weight: 500;
        transition: 0.3s;
    }
    .stButton > button:hover{
        background: var(--accent);
        color: #FFFFFF;
        border-color: var(--accent);
    }

    /* Footer */
    .footerline{
        margin-top: 26px;
        padding-top: 14px;
        border-top: 1px solid #EEE;
        color: #999;
        font-size: 0.86rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        text-align: center;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 3. ROBUST CLOUD LOADER ---
def run_cloud_safely():
    """Runs the cloud module safely, ignoring set_page_config conflicts."""
    file_path = os.path.join("cloud", "cloud_cal.py")
    if not os.path.exists(file_path):
        st.error(f"❌ File not found: {file_path}")
        return

    original_config = st.set_page_config
    st.set_page_config = lambda *args, **kwargs: None
    
    try:
        with open(file_path, "r") as f:
            code = f.read()
            local_scope = {}
            exec(code, local_scope)
            if "run_cloud_ui" in local_scope:
                local_scope["run_cloud_ui"]()
            elif "main" in local_scope:
                local_scope["main"]()
    except Exception as e:
        st.error(f"⚠️ Cloud Module Error: {e}")
    finally:
        st.set_page_config = original_config


# --- 4. STATE: ASSUMPTIONS ---
def init_assumptions():
    if "assumptions" in st.session_state:
        return

    st.session_state["assumptions"] = {
        "carbon_factors": {
            "source": "To be validated with LVMH (recommended: official carbon factor database / internal methodology).",
            "device_manufacturing_tco2e": {
                "Laptop": None,
                "Smartphone": None,
                "Screen": None,
                "Tablet": None,
                "Switch/Router": None,
            },
        },
        "device_lifespan_targets_months": {
            "Laptop": 72,
            "Smartphone": 60,
            "Screen": 84,
            "Tablet": 72,
            "Switch/Router": 72,
            "Refurbished smartphone": 24,
            "Refurbished screen": 84,
            "Refurbished switch/router": 84,
        },
        "electricity_carbon_intensity": {
            "definition": "kgCO2e per kWh (proxy for energy mix by country).",
            "by_country": {
                "France": None,
                "Italy": None,
                "United States": None,
                "China": None,
                "Custom": None,
            }
        },
        "cloud": {
            "carbon_intensity_assumption": "Cloud CO2 is estimated from storage volume + energy factor + electricity CI (proxy).",
            "storage_energy_kwh_per_gb_month": None,
            "provider_ci_override": {
                "AWS": None,
                "Azure": None,
                "GCP": None,
            }
        }
    }


def render_assumptions_drawer(scope_hint: str = "Global"):
    init_assumptions()
    A = st.session_state["assumptions"]

    st.markdown("### Assumptions")
    st.caption("Transparent, configurable inputs to make ROI defensible (consulting-grade).")

    with st.expander("Open assumptions (methodology inputs)", expanded=False):
        st.markdown("#### Carbon factors")
        st.write(A["carbon_factors"]["source"])
        st.caption("Manufacturing factors (tCO₂e/device) are shown as placeholders unless validated/provided.")

        for k, v in A["carbon_factors"]["device_manufacturing_tco2e"].items():
            st.write(f"- **{k}**: {v if v is not None else 'TBD'}")

        st.markdown("#### Device lifespan targets (months)")
        lf = A["device_lifespan_targets_months"]
        for k, v in lf.items():
            st.write(f"- **{k}**: {v}")

        st.markdown("#### Energy mix by country (proxy)")
        st.caption(A["electricity_carbon_intensity"]["definition"])
        
        # Editable section
        st.markdown("#### Edit key assumptions (demo)")
        colA, colB = st.columns(2)

        with colA:
            country = st.selectbox("Country (for electricity CI)", list(A["electricity_carbon_intensity"]["by_country"].keys()), index=0)
            current_ci = A["electricity_carbon_intensity"]["by_country"].get(country)
            new_ci = st.number_input(
                "Electricity CI (kgCO₂e/kWh)",
                min_value=0.0, value=float(current_ci) if current_ci is not None else 0.0,
                step=0.01,
                help="Set to 0 if unknown."
            )
            A["electricity_carbon_intensity"]["by_country"][country] = new_ci if new_ci > 0 else None

        with colB:
            current_kwh = A["cloud"]["storage_energy_kwh_per_gb_month"]
            new_kwh = st.number_input(
                "Cloud storage energy (kWh/GB-mo)",
                min_value=0.0, value=float(current_kwh) if current_kwh is not None else 0.0,
                step=0.0001,
                format="%.4f"
            )
            A["cloud"]["storage_energy_kwh_per_gb_month"] = new_kwh if new_kwh > 0 else None

    # Red flags
    missing = []
    if A["cloud"]["storage_energy_kwh_per_gb_month"] is None and scope_hint in ("Cloud", "Global"):
        missing.append("Cloud storage energy factor is not set.")
    if all(v is None for v in A["electricity_carbon_intensity"]["by_country"].values()):
        missing.append("No electricity carbon intensity is set.")

    if missing:
        st.warning("Assumptions to validate:\n- " + "\n- ".join(missing))


def render_footer():
    st.markdown(
        "<div class='footerline'>In collaboration with Albert School • Mines Paris – PSL</div>",
        unsafe_allow_html=True
    )


# --- 5. NAV + HEADER ---
def _logo_path(primary_folder_file: str, fallback_root_file: str) -> str | None:
    if os.path.exists(primary_folder_file):
        return primary_folder_file
    if os.path.exists(fallback_root_file):
        return fallback_root_file
    return None


def go_to(page_name: str):
    st.session_state["pending_mode"] = page_name
    st.rerun()


def render_header_lvmh_only():
    left, center, right = st.columns([1.6, 6, 1.0], gap="large")

    with left:
        path_lvmh = _logo_path(os.path.join("logo.png", "lvmh_logo.png"), "lvmh_logo.png")
        
        # Premium badge - Light beige/white background
        st.markdown(
            """
            <div style="
                display:inline-block;
                padding:14px 18px;
                border-radius:18px;
                background: #F8F5F2;
                border:1px solid rgba(138,108,74,0.3);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                position: relative;
                overflow: hidden;
            ">
            """,
            unsafe_allow_html=True
        )

        if path_lvmh:
            st.image(path_lvmh, width=140)
        else:
            st.markdown(
                "<div style='font-family:Playfair Display,serif;color:#8a6c4a;letter-spacing:1px;font-size:1.35rem;'>LVMH</div>",
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with center:
        st.markdown("<div class='header-title'>Green in Tech • Decision Support Platform</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-sub'>Equipment & Cloud Storage</div>", unsafe_allow_html=True)

    with right:
        st.write("")

    st.markdown("<div class='topline'></div>", unsafe_allow_html=True)


# --- 6. UI BLOCKS ---
def show_homepage():
    st.markdown(
        "<div class='hero'>"
        "<div class='hero-title'>Sustainable IT Cockpit</div>"
        "<div class='hero-sub'>LVMH Digital • Green in Tech Decision Support</div>"
        "<div class='hero-row'>"
        "<div class='chip'>Decision support — not execution</div>"
        "<div class='chip'>Financial + CO₂ + Organizational ROI</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("IT Carbon Footprint", "4,102 tCO₂e", "-5% YoY")
    with c2: st.metric("Active Assets", "14,205", "+12%")
    with c3: st.metric("Energy Efficiency", "85%", "+2 pts")
    with c4: st.metric("Reconditioning Rate", "32%", "+5%")

    st.markdown("<br>", unsafe_allow_html=True)

    col_ctx, col_obj = st.columns(2, gap="large")
    with col_ctx:
        st.markdown("""
        <div class="card">
          <div class="card-title">🌍 Context</div>
          <div class="divider"></div>
          <p>
            A decision cockpit to consolidate signals across Maisons and support prioritization of Green IT actions.
          </p>
          <p class="card-meta">Scope: equipment lifecycle + cloud storage scenarios.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_obj:
        st.markdown("""
        <div class="card">
          <div class="card-title">🎯 What the platform delivers</div>
          <div class="divider"></div>
          <ul>
            <li><b>Per-asset recommendation</b> (Keep / Refurbish / Recycle)</li>
            <li><b>Scenario comparison</b> (policy & assumptions)</li>
            <li><b>Prioritized roadmap</b> (ROI, impact, scalability)</li>
          </ul>
          <p class="card-meta">Outputs are estimates driven by explicit assumptions.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Select a module")
    st.markdown("<div class='small-muted'>Run analyses, compare scenarios, and generate recommendations.</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2 = st.columns(2, gap="large")
    with m1:
        st.markdown("""
        <div class="card">
          <div class="card-title">💻 Equipment Audit</div>
          <div class="divider"></div>
          <p>
            Inventory analysis (CSV) + policy simulations to estimate cost, CO₂ and feasibility.
          </p>
          <p class="card-meta">Includes: refurb vs new, lease vs buy, lifecycle extension, ranking.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Equipment Audit →", use_container_width=True):
            go_to("Equipment Audit")

    with m2:
        st.markdown("""
        <div class="card">
          <div class="card-title">☁️ Cloud Analytics</div>
          <div class="divider"></div>
          <p>
            Storage decision support: retention scenarios and provider comparison by country.
          </p>
          <p class="card-meta">No automated deletion. Recommendations only.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Cloud Analytics →", use_container_width=True):
            go_to("Cloud Analytics")


def page_context(title: str, left_title: str, left_body: str, right_title: str, right_body: str):
    st.markdown(f"## {title}")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">{left_title}</div>
          <div class="divider"></div>
          <p>{left_body}</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">{right_title}</div>
          <div class="divider"></div>
          <p>{right_body}</p>
        </div>
        """, unsafe_allow_html=True)


# --- 7. MAIN CONTROLLER ---
def main():
    # Handle Navigation State
    if "app_mode" not in st.session_state:
        st.session_state["app_mode"] = "Home"
    if "pending_mode" in st.session_state:
        st.session_state["app_mode"] = st.session_state.pop("pending_mode")

    # --- SIDEBAR NAV ---
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size: 0.78rem; color: #999; margin-bottom: 6px; letter-spacing:2px; text-transform:uppercase;'>Navigation</p>",
            unsafe_allow_html=True
        )
        st.radio(
            "Nav",
            ["Home", "Equipment Audit", "Cloud Analytics"],
            key="app_mode",
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.caption("LVMH • Green in Tech")
        st.caption("Decision Support Platform | v1.0")

    # --- MAIN CONTENT ---
    render_header_lvmh_only()

    content_col, assumptions_col = st.columns([3.2, 1.2], gap="large")
    app_mode = st.session_state["app_mode"]

    with content_col:
        if app_mode == "Home":
            show_homepage()

        elif app_mode == "Equipment Audit":
            page_context(
                "Equipment Lifecycle & ROI",
                "Why this matters",
                "Device manufacturing and replacement cycles are key drivers of IT footprint. "
                "This module identifies where circularity generates the best combined value (cost + CO₂ + feasibility).",
                "What you can do here",
                "Upload an inventory to get per-asset recommendations, or run simulations to compare policies and generate a prioritized roadmap."
            )
            st.markdown("<br>", unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["INTELLIGENT AUDIT", "PREDICTIVE SIMULATION"])
            with tab1:
                page_context(
                    "Intelligent Audit (Inventory → Recommendations)",
                    "Inputs",
                    "Upload a standardized CSV. The tool evaluates items line-by-line.",
                    "Outputs",
                    "Keep / Refurbish / Recycle recommendation per asset with a transparent ROI breakdown."
                )
                st.markdown("<br>", unsafe_allow_html=True)
                try:
                    from equipement_audit.audit_ui import run_audit_ui
                    run_audit_ui()
                except ImportError:
                    st.error("Audit module missing.")

            with tab2:
                page_context(
                    "Predictive Simulation (Policy Scenarios → Action Ranking)",
                    "Simulation logic",
                    "Compare policy scenarios (baseline vs alternatives). Scoring stays assumption-driven for executive governance.",
                    "Roadmap output",
                    "Ranked actions based on Financial ROI, Environmental ROI and Organizational feasibility."
                )
                st.markdown("<br>", unsafe_allow_html=True)
                try:
                    from equipement_simulation.simulation_ui import run_simulation_ui
                    run_simulation_ui()
                except ImportError:
                    st.info("Simulation initializing...")

        elif app_mode == "Cloud Analytics":
            page_context(
                "Cloud Storage Decision Support",
                "Context",
                "Cloud storage growth drives both cost and emissions. This module provides scenario-based estimates for prioritization.",
                "What you can do here",
                "Compare provider options by country and test retention scenarios to estimate data reduction required to meet CO₂ objectives."
            )
            st.markdown("<br>", unsafe_allow_html=True)

            st.title("Cloud Emissions")
            st.markdown("---")
            run_cloud_safely()

        render_footer()

    with assumptions_col:
        scope = "Equipment" if app_mode == "Equipment Audit" else ("Cloud" if app_mode == "Cloud Analytics" else "Global")
        render_assumptions_drawer(scope_hint=scope)


if __name__ == "__main__":
    main()