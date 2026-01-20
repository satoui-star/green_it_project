import streamlit as st
import plotly.graph_objects as go
from utils_ui import inject_global_styles, render_logo, render_footer
from cloud_cal import (
    get_cloud_providers, calculate_carbon_intensity, 
    calculate_baseline_metrics, calculate_archival_strategy
)

def run_cloud_optimizer():
    # 1. LOAD MASTER STYLES & HEADER
    inject_global_styles()
    render_logo()

    st.title("Cloud Storage Sustainability Advisor")
    
    # Settings Section
    with st.container():
        st.subheader("Configuration")
        c1, c2, c3 = st.columns(3)
        with c1:
            providers = st.multiselect("Cloud Providers", options=get_cloud_providers(), default=["AWS"])
        with c2:
            storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0)
        with c3:
            reduction_target = st.slider("Reduction Target (%)", 5, 80, 30)
    
    # Logic
    storage_gb = storage_tb * 1024
    intensity = calculate_carbon_intensity(providers)
    baseline = calculate_baseline_metrics(storage_gb, intensity)
    archival_df = calculate_archival_strategy(storage_gb, reduction_target, 15, intensity, 5)
    
    # --- ENHANCED ACTION BOX (RED) ---
    st.markdown("<br>", unsafe_allow_html=True)
    year_1_archive = archival_df.iloc[0]['Data to Archive (TB)']
    
    if year_1_archive > 0:
        st.markdown(f"""
        <div class="action-box-red">
            <div class="action-box-icon">🚨</div>
            <div class="action-box-content">
                <div class="action-box-title">Immediate Action Required</div>
                <p class="action-box-desc">
                    To maintain your <b>{reduction_target}%</b> sustainability target, you must archive 
                    <span style="font-weight:700;color:#DC2626;">{year_1_archive:.1f} TB</span> of data this year. 
                    Delaying this action will result in an unrecoverable carbon gap.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Charts / KPIs
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""<div class="kpi-card"><h3>Baseline Emissions</h3><div class="kpi-value">{baseline['emissions']:,.0f}</div><p>kg CO₂ / year</p></div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""<div class="kpi-card"><h3>Water Footprint</h3><div class="kpi-value">{baseline['water_liters']:,.0f}</div><p>Liters / year</p></div>""", unsafe_allow_html=True)

    # 2. RENDER FOOTER
    render_footer()

if __name__ == "__main__":
    run_cloud_optimizer()
