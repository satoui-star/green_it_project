import streamlit as st
import plotly.graph_objects as go
from utils_ui import inject_global_styles, render_logo, render_footer
from cloud_cal import (
    get_cloud_providers, calculate_carbon_intensity, 
    calculate_baseline_metrics, calculate_archival_strategy
)

def run_cloud_optimizer():
    # 1. Initialize branding and styles
    inject_global_styles()
    render_logo()

    st.title("Cloud Storage Sustainability Advisor")
    
    # Configuration Column Inputs
    st.subheader("Settings")
    c1, c2, c3 = st.columns(3)
    with c1:
        providers = st.multiselect("Cloud Providers", options=get_cloud_providers(), default=["AWS"])
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0)
    with c3:
        target = st.slider("Reduction Target (%)", 5, 80, 30)

    # Logic Calculations
    intensity = calculate_carbon_intensity(providers)
    archival_df = calculate_archival_strategy(storage_tb*1024, target, 15, intensity, 5)
    year_1_archive = archival_df.iloc[0]['Data to Archive (TB)']

    # 2. ENHANCED RED ACTION BOX (Matches your screenshot design)
    if year_1_archive > 0:
        st.markdown(f"""
        <div class="action-box-red">
            <div class="action-box-icon">🚨</div>
            <div class="action-box-content">
                <div class="action-box-title">Immediate Action Required</div>
                <p class="action-box-text">
                    To maintain your <b>{target}%</b> sustainability target, you must archive 
                    <span style="font-weight:700;color:#DC2626;">{year_1_archive:.1f} TB</span> 
                    of data this year. Delaying action will widen the carbon waste gap.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Display Charts/KPIs below the action box
    st.markdown("### Environmental Impact Analysis")
    # ... your chart calls here ...

    # 3. Footer
    render_footer()

if __name__ == "__main__":
    run_cloud_optimizer()
