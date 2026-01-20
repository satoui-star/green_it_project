import streamlit as st
import plotly.graph_objects as go
import os
import base64

# === IMPORTANT: THIS IS THE IMPORT FROM YOUR UTILS_UI FILE ===
from utils_ui import inject_global_styles, render_logo, render_footer

from cloud_cal import (
    get_cloud_providers,
    calculate_carbon_intensity,
    calculate_baseline_metrics,
    calculate_archival_strategy,
    calculate_cumulative_savings,
    LITERS_PER_SHOWER,
    CO2_PER_TREE_PER_YEAR
)

# 2. Inject the Shared CSS immediately so it applies to the whole page
inject_global_styles()

def render_metric_card(label, value, equivalent_text, equivalent_emoji, help_text=""):
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{equivalent_emoji}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-unit">~{equivalent_text}</div>
        </div>
    """, unsafe_allow_html=True)

# YOUR ORIGINAL CSS - PRESERVED UNCHANGED
st.markdown("""
    <style>
    /* ... [Keeping all your original CSS here exactly as it was] ... */
    </style>
    """, unsafe_allow_html=True)

def create_diverging_path_chart(archival_df, reduction_target):
    # (Your chart logic remains unchanged)
    fig = go.Figure()
    # ...
    return fig

def run_cloud_optimizer():
    """Main logic for the Cloud UI"""
    
    # 3. DISPLAY THE COMMON HEADER (Logo & Tagline)
    render_logo()

    st.title("Cloud Storage Sustainability Advisor")
    st.write("Optimize your data center footprint through intelligent archival strategies.")

    st.subheader("Settings")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        selected_providers = st.multiselect("Cloud Providers", options=get_cloud_providers(), default=["AWS"])
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c3:
        reduction_target = st.slider("CO₂ Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.number_input("Projection Period (Years)", 1, 10, 5)
    with c5:
        data_growth_rate = st.slider("Data Growth Rate (%/year)", 0, 50, 15)

    storage_gb = storage_tb * 1024
    carbon_intensity = calculate_carbon_intensity(selected_providers)
    baseline = calculate_baseline_metrics(storage_gb, carbon_intensity)

    st.divider()
    st.subheader("Current Annual Baseline")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card("Annual Carbon Footprint", f"{baseline['emissions']:,.0f} kg CO₂", f"{baseline['trees']:,.0f} Trees", "🌳")
    with m2:
        render_metric_card("Annual Water Usage", f"{baseline['water_liters']:,.0f} Liters", f"{baseline['showers']:,.0f} Showers", "🚿")
    with m3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Efficiency Goal</div>
            <div class="kpi-value" style="color: #059669;">-{reduction_target}%</div>
            <div class="kpi-unit">Relative reduction vs growth</div>
        </div>""", unsafe_allow_html=True)

    # --- ACTION ALERT ---
    archival_df = calculate_archival_strategy(storage_gb, reduction_target, data_growth_rate, carbon_intensity, projection_years)
    year_1 = archival_df.iloc[0]
    st.markdown(f"""<div class="urgent-alert"><h3>Immediate Intervention Required</h3>
    <p>Archive <b>{year_1['Data to Archive (TB)']:.1f} TB</b> this year.</p></div>""", unsafe_allow_html=True)

    # --- CHART ---
    st.plotly_chart(create_diverging_path_chart(archival_df, reduction_target), use_container_width=True)

    # 4. DISPLAY THE COMMON FOOTER (Divider & Copyright)
    render_footer()

def render_cloud_section():
    run_cloud_optimizer()

def run():
    run_cloud_optimizer()

if __name__ == "__main__":
    run_cloud_optimizer()
