import streamlit as st
import os
import sys

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LVMH Sustainable IT",
    page_icon="⚜️",
    layout="wide"
)

# --- 2. LUXURY DESIGN SYSTEM (LVMH vibe + #8a6c4a) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Inter:wght@300;400;600&display=swap');

    :root{
        --bg:#ffffff;
        --border:rgba(255,255,255,0.08);
        --muted:#A3A3A3;
        --accent:#8a6c4a;
        --accentSoft:rgba(138,108,74,0.16);
        --accentLine:rgba(138,108,74,0.40);
    }

    .stApp{
        background:
            radial-gradient(1100px 560px at 18% -8%, rgba(138,108,74,0.14), transparent 60%),
            radial-gradient(900px 520px at 92% 0%, rgba(138,108,74,0.08), transparent 62%),
            var(--bg);
        color:#ECECEC;
    }
    section[data-testid="stMain"]{ padding-top: 0.8rem; }

    h1,h2,h3{
        font-family:'Playfair Display',serif!important;
        color:var(--accent)!important;
        letter-spacing:0.5px;
    }
    p,div,label,li,.stMarkdown{
        font-family:'Inter',sans-serif;
        font-weight:300;
        line-height:1.65;
    }
    .small-muted{ color:var(--muted); font-size:0.95rem; }

    /* Sidebar: quieter */
    [data-testid="stSidebar"]{
        background: linear-gradient(180deg, #0f0f0f, #0a0a0a);
        border-right: 1px solid rgba(255,255,255,0.06);
        opacity: 0.96;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; }

    /* Header */
    .topline{
        height: 1px;
        background: linear-gradient(90deg, rgba(138,108,74,0.45), rgba(42,42,42,0.00));
        margin: 12px 0 18px 0;
    }
    .header-title{
        font-family:'Playfair Display',serif;
        color: var(--accent);
        font-size: 1.02rem;
        text-align:center;
        margin-top: 2px;
    }
    .header-sub{
        color: var(--muted);
        font-size: 0.82rem;
        letter-spacing: 2.2px;
        text-transform: uppercase;
        text-align:center;
        margin-top: 2px;
    }

    /* Hero */
    .hero{
        background: linear-gradient(135deg, var(--accentSoft), rgba(255,255,255,0.01));
        border: 1px solid var(--accentLine);
        border-radius: 16px;
        padding: 28px 28px 20px 28px;
    }
    .hero-title{ font-size: 2.65rem; margin: 0; }
    .hero-sub{
        margin-top: 10px;
        color: var(--muted);
        letter-spacing: 2.4px;
        text-transform: uppercase;
        font-size: .82rem;
    }
    .hero-row{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
    .chip{
        border: 1px solid rgba(138,108,74,0.33);
        background: rgba(0,0,0,0.26);
        color: #EAEAEA;
        padding: 7px 11px;
        border-radius: 999px;
        font-size: .83rem;
    }

    /* Cards */
    .card{
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.00));
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        height: 100%;
    }
    .card:hover{
        border-color: rgba(138,108,74,0.40);
        box-shadow: 0 12px 34px rgba(0,0,0,0.36);
        transform: translateY(-1px);
        transition: all .18s ease;
    }
    .card-title{
        display:flex; align-items:center; gap:10px;
        color: var(--accent);
        font-family:'Playfair Display',serif;
        font-size: 1.18rem;
        margin: 0 0 10px 0;
    }
    .divider{
        height:1px;
        background: linear-gradient(90deg, rgba(138,108,74,0.42), rgba(42,42,42,0.0));
        margin: 10px 0 12px 0;
    }
    .card-meta{ color: var(--muted); font-size: .9rem; margin: 0; }

    /* Metrics */
    div[data-testid="stMetric"]{
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 3px solid var(--accent);
        padding: 12px 14px;
        border-radius: 14px;
    }
    div[data-testid="stMetricLabel"]{ color: var(--accent)!important; font-size: 0.84rem; }
    div[data-testid="stMetricValue"]{
        color: #fff!important;
        font-family:'Playfair Display',serif!important;
        font-size: 1.55rem !important;
        white-space: nowrap;
    }

    /* Buttons */
    .stButton > button{
        background: linear-gradient(180deg, rgba(138,108,74,0.18), rgba(138,108,74,0.04));
        border: 1px solid rgba(138,108,74,0.55);
        color: var(--accent);
        border-radius: 12px;
        padding: 0.58rem 0.92rem;
    }
    .stButton > button:hover{
        background: var(--accent);
        color: #0A0A0A;
        border-color: var(--accent);
    }

    /* Footer */
    .footerline{
        margin-top: 26px;
        padding-top: 14px;
        border-top: 1px solid rgba(255,255,255,0.06);
        color: rgba(255,255,255,0.45);
        font-size: 0.86rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        text-align: center;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 3. ROBUST CLOUD LOADER (Preserved EXACTLY as provided) ---
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


# --- 4. STATE: ASSUMPTIONS (explicit + editable) ---
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
            "storage_energy_kwh_per_gb_month": None,  # keep explicit; user sets demo value
            "provider_ci_override": {  # optional
                "AWS": None,
                "Azure": None,
                "GCP": None,
            }
        }
    }


def render_assumptions_drawer(scope_hint: str = "Global"):
    """
    Right-column drawer: explicit assumptions, editable.
    scope_hint can be "Global", "Equipment", "Cloud".
    """
    init_assumptions()
    A = st.session_state["assumptions"]

    st.markdown("### Assumptions")
    st.caption("Transparent, configurable inputs to make ROI defensible (consulting-grade).")

    with st.expander("Open assumptions (methodology inputs)", expanded=False):
        st.markdown("#### Carbon factors")
        st.write(A["carbon_factors"]["source"])
        st.caption("Manufacturing factors (tCO₂e/device) are shown as placeholders unless validated/provided.")

        # show placeholders
        for k, v in A["carbon_factors"]["device_manufacturing_tco2e"].items():
            st.write(f"- **{k}**: {v if v is not None else 'TBD'}")

        st.markdown("#### Device lifespan targets (months)")
        lf = A["device_lifespan_targets_months"]
        for k, v in lf.items():
            st.write(f"- **{k}**: {v}")

        st.markdown("#### Energy mix by country (proxy)")
        st.caption(A["electricity_carbon_intensity"]["definition"])
        st.write("Electricity carbon intensity (kgCO₂e/kWh) — used for equipment energy and cloud storage estimates.")

        # editable section
        st.markdown("#### Edit key assumptions (demo / adjustable)")
        colA, colB = st.columns(2)

        with colA:
            country = st.selectbox("Country (for electricity CI)", list(A["electricity_carbon_intensity"]["by_country"].keys()), index=0)
            current_ci = A["electricity_carbon_intensity"]["by_country"].get(country)
            new_ci = st.number_input(
                "Electricity CI (kgCO₂e/kWh)",
                min_value=0.0, value=float(current_ci) if current_ci is not None else 0.0,
                step=0.01,
                help="Set to 0 if unknown. Ideally replace with official country-specific data."
            )
            A["electricity_carbon_intensity"]["by_country"][country] = new_ci if new_ci > 0 else None

        with colB:
            current_kwh = A["cloud"]["storage_energy_kwh_per_gb_month"]
            new_kwh = st.number_input(
                "Cloud storage energy factor (kWh / GB-month)",
                min_value=0.0, value=float(current_kwh) if current_kwh is not None else 0.0,
                step=0.0001,
                format="%.4f",
                help="Used to estimate storage energy consumption. Replace with validated benchmark/provider data."
            )
            A["cloud"]["storage_energy_kwh_per_gb_month"] = new_kwh if new_kwh > 0 else None

            provider = st.selectbox("Provider CI override (optional)", ["AWS", "Azure", "GCP"])
            current_p = A["cloud"]["provider_ci_override"].get(provider)
            new_p = st.number_input(
                "Provider electricity CI override (kgCO₂e/kWh)",
                min_value=0.0, value=float(current_p) if current_p is not None else 0.0,
                step=0.01,
                help="Optional override if provider/location has a specific carbon intensity."
            )
            A["cloud"]["provider_ci_override"][provider] = new_p if new_p > 0 else None

        st.markdown("#### Cloud carbon intensity assumptions")
        st.write(A["cloud"]["carbon_intensity_assumption"])

    # Optional: quick “red flags” (consulting vibe)
    missing = []
    if A["cloud"]["storage_energy_kwh_per_gb_month"] is None and scope_hint in ("Cloud", "Global"):
        missing.append("Cloud storage energy factor is not set (kWh/GB-month).")
    if all(v is None for v in A["electricity_carbon_intensity"]["by_country"].values()):
        missing.append("No electricity carbon intensity is set for any country.")

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

        # Premium badge (bigger + more elegant)
        st.markdown(
            """
            <div style="
                display:inline-block;
                padding:14px 18px;
                border-radius:18px;
                background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0.10));
                border:1px solid rgba(138,108,74,0.42);
                box-shadow: 0 18px 44px rgba(0,0,0,0.45);
                position: relative;
                overflow: hidden;
            ">
              <div style="
                position:absolute; top:0; left:0; right:0; height:1px;
                background: linear-gradient(90deg, rgba(138,108,74,0.00), rgba(138,108,74,0.55), rgba(138,108,74,0.00));
              "></div>
            """,
            unsafe_allow_html=True
        )

        if path_lvmh:
            # Bigger logo, fixed width for consistency
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
    # Apply pending navigation BEFORE sidebar radio instantiation
    if "app_mode" not in st.session_state:
        st.session_state["app_mode"] = "Home"
    if "pending_mode" in st.session_state:
        st.session_state["app_mode"] = st.session_state.pop("pending_mode")

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

    # Header: LVMH only (Option A)
    render_header_lvmh_only()

    # Main layout: content (left) + assumptions drawer (right)
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
                    "Upload a standardized CSV (device type, age, procurement mode, costs, energy). The tool evaluates items line-by-line.",
                    "Outputs",
                    "Keep / Refurbish / Recycle recommendation per asset with a transparent ROI breakdown. Exportable results and hotspot views."
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
                    "Compare 5–6 policy scenarios (baseline vs alternatives). The scoring stays assumption-driven for executive governance.",
                    "Roadmap output",
                    "Ranked actions based on Financial ROI, Environmental ROI and Organizational feasibility to prioritize the fastest path to objectives."
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
                "Cloud storage growth (including dark data) drives both cost and emissions. This module provides scenario-based estimates for prioritization.",
                "What you can do here",
                "Compare provider options by country and test retention scenarios to estimate the data reduction required to meet CO₂ objectives (1–5 years)."
            )
            st.markdown("<br>", unsafe_allow_html=True)

            st.title("Cloud Emissions")
            st.markdown("---")
            run_cloud_safely()

        # Footer (partners moved here)
        render_footer()

    with assumptions_col:
        scope = "Equipment" if app_mode == "Equipment Audit" else ("Cloud" if app_mode == "Cloud Analytics" else "Global")
        render_assumptions_drawer(scope_hint=scope)


if __name__ == "__main__":
    main()

