import streamlit as st
import plotly.graph_objects as go
import os
import base64

# Import from your utils_ui file
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

# 1. Page Setup
st.set_page_config(
    page_title="Green IT Decision Portal",
    page_icon="🌱",
    layout="wide"
)

# 2. Inject Global Styles (Fonts, Expanders, etc.)
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

# === CSS BLOCK (Original + New Action Box Styles) ===
st.markdown("""
    <style>
    /* === LIGHT LUXURY BASE === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === COMPLETELY HIDE EXPANDER ARROWS === */
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
    
    [data-testid="stExpander"] summary > span:first-child,
    [data-testid="stExpander"] details > summary > div:first-child {
        display: none !important;
    }
    
    details summary {
        list-style: none !important;
        list-style-type: none !important;
    }
    
    details summary::-webkit-details-marker,
    details summary::marker {
        display: none !important;
        content: "" !important;
        font-size: 0 !important;
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
    
    [data-testid="stExpander"] > details > summary:hover {
        color: #6d553a !important;
        background: #faf8f5 !important;
    }
    
    [data-testid="stExpander"] > details[open] > summary {
        border-bottom: 1px solid #e8e4dc !important;
    }
    
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #fdfcfa !important;
        padding: 18px !important;
    }
    
    /* === TYPOGRAPHY === */
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
    
    /* === KPI CARDS === */
    .kpi-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 35px 25px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06);
        transition: all 0.3s ease;
        position: relative;
        height: 100%;
        margin-bottom: 15px;
    }
    
    .kpi-card:hover {
        box-shadow: 0 8px 30px rgba(138, 108, 74, 0.12);
        transform: translateY(-3px);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 3px 3px;
    }
    
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 12px;
        color: #8a6c4a;
    }
    
    .kpi-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.65rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
        font-weight: 500;
    }
    
    .kpi-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.8rem;
        font-weight: 500;
        color: #2c2c2c;
        line-height: 1;
        margin-bottom: 12px;
    }
    
    .kpi-unit {
        font-family: 'Montserrat', sans-serif;
        font-size: 1rem;
        color: #8a6c4a;
        font-weight: 400;
    }
    
    /* === CONTEXT SECTION === */
    .context-card {
        background: #fff;
        border-left: 3px solid #8a6c4a;
        border-radius: 0 8px 8px 0;
        padding: 25px 30px;
        margin: 18px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    
    .context-title {
        font-family: 'Montserrat', sans-serif;
        color: #8a6c4a;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .context-text {
        font-family: 'Cormorant Garamond', serif;
        color: #555;
        line-height: 1.8;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* === INSIGHT CARDS === */
    .insight-card {
        background: linear-gradient(135deg, #f0f7f1 0%, #fff 100%);
        border: 1px solid #c8e6c9;
        border-radius: 8px;
        padding: 24px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.1);
    }
    
    .insight-title {
        font-family: 'Montserrat', sans-serif;
        color: #2e7d32;
        font-weight: 600;
        font-size: 0.7rem;
        margin-bottom: 12px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .insight-text {
        font-family: 'Cormorant Garamond', serif;
        color: #555;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* === NEW ENHANCED RED ACTION BOX === */
    .action-box-red {
        background-color: #FEF2F2; /* Light red background */
        border: 1px solid #F87171; /* Red border */
        border-left: 8px solid #DC2626; /* Thick red left border */
        border-radius: 8px;
        padding: 25px;
        margin: 35px 0;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.1);
        display: flex;
        align-items: flex-start;
        gap: 20px;
    }

    .action-box-icon {
        font-size: 2.5rem;
        color: #DC2626;
        line-height: 1;
        margin-top: -4px;
    }

    .action-box-content h3 {
        color: #991B1B !important; /* Dark red title */
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin: 0 0 10px 0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .action-box-content p {
        color: #7F1D1D !important; /* Dark red text */
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
        margin: 0 !important;
    }

    .action-highlight {
         font-weight: 700;
         color: #DC2626;
         font-size: 1.25rem;
    }
    
    /* === DIVIDERS === */
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #d4cfc5, transparent);
        margin: 50px 0;
    }
    
    /* === CHART CONTAINER === */
    .chart-container {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    /* === STREAMLIT OVERRIDES === */
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
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: #6d553a !important;
        box-shadow: 0 6px 20px rgba(138, 108, 74, 0.25) !important;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background: #fff !important;
        border: 1px solid #d4cfc5 !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stNumberInput"] > div > div > input {
        background: #fff !important;
        border: 1px solid #d4cfc5 !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stSlider"] > div > div > div {
        background: #8a6c4a !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #2c2c2c !important;
        font-family: 'Playfair Display', serif !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #888 !important;
    }
    
    [data-testid="stAlert"] {
        background: #faf8f5 !important;
        border: 1px solid #e8e4dc !important;
        color: #555 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def create_diverging_path_chart(archival_df, reduction_target):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions w/o Archival (kg)'],
        name='Without Action',
        line=dict(color='#ef4444', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='x'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions After Archival (kg)'],
        name='With Strategic Archival',
        line=dict(color='#10b981', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=archival_df['Year'].tolist() + archival_df['Year'].tolist()[::-1],
        y=archival_df['Emissions w/o Archival (kg)'].tolist() + 
          archival_df['Emissions After Archival (kg)'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(239, 68, 68, 0.2)',
        line=dict(width=0),
        showlegend=True,
        name='Carbon Waste Gap',
        hoverinfo='skip'
    ))
    
    total_gap = (archival_df['Emissions w/o Archival (kg)'] - 
                 archival_df['Emissions After Archival (kg)']).sum()
    
    mid_year = len(archival_df) // 2
    mid_y = (archival_df['Emissions w/o Archival (kg)'].iloc[mid_year] + 
             archival_df['Emissions After Archival (kg)'].iloc[mid_year]) / 2
    
    fig.add_annotation(
        x=archival_df['Year'].iloc[mid_year],
        y=mid_y,
        text=f"<b>Total Avoidable<br>Emissions:<br>{total_gap:,.0f} kg CO₂</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#991b1b",
        ax=-80,
        ay=-40,
        font=dict(size=14, color="#991b1b", family="Arial Black"),
        bgcolor="rgba(254, 242, 242, 0.95)",
        bordercolor="#ef4444",
        borderwidth=2,
        borderpad=8
    )
    
    fig.update_layout(
        title={
            'text': '<b>The Diverging Paths: Action vs Inaction</b><br><sub>Every year of delay widens the sustainability gap</sub>',
            'font': {'size': 20, 'color': '#1e293b'}
        },
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Annual CO₂ Emissions (kg)</b>",
        height=550,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        plot_bgcolor='#f8fafc',
        paper_bgcolor='white'
    )
    
    return fig

def run_cloud_optimizer():
    """Main logic for the Cloud UI"""
    
    # 3. DISPLAY HEADER
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

    # --- CALCULATE STRATEGY ---
    archival_df = calculate_archival_strategy(storage_gb, reduction_target, data_growth_rate, carbon_intensity, projection_years)
    year_1 = archival_df.iloc[0]
    data_to_archive = year_1['Data to Archive (TB)']

    # --- ENHANCED ACTION REQUIRED SECTION ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    if data_to_archive > 0.01: # Show alert if action is needed
        st.markdown(f"""
        <div class="action-box-red">
            <div class="action-box-icon">
                🚨
            </div>
            <div class="action-box-content">
                <h3>Immediate Action Required</h3>
                <p>
                    To maintain your <b>{reduction_target}%</b> efficiency target against projected growth, you must archive
                    <span class="action-highlight">{data_to_archive:.1f} TB</span> of data this year.
                    Failure to act will result in exceeding your baseline emissions.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("✅ Current trajectory meets efficiency targets based on inputs. No immediate archival required this year.")

    # --- CHART & TABLES ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f" Total {projection_years}-Year Environmental Gap")
    cumulative = calculate_cumulative_savings(archival_df)

    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card("Total CO₂ Saved", f"{cumulative['co2_saved']:,.0f} kg CO₂", f"{cumulative['trees_equivalent']:,.0f} Trees", "🌳")
    with k2:
        render_metric_card("Total Water Reclaimed", f"{cumulative['water_saved']:,.0f} Liters", f"{cumulative['showers_saved']:,.0f} Showers", "🚿")
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Total Financial ROI</div>
            <div class="kpi-value">€{cumulative['euro_saved']:,.0f}</div>
            <div class="kpi-unit">Avoided Costs over {projection_years}y</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("### Visual Impact Analysis")
    st.caption("Diverging path visualization showing the magnitude and urgency of action")
    
    st.plotly_chart(create_diverging_path_chart(archival_df, reduction_target), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📊 View Technical Breakdown & Data Evolution"):
        # (Table display logic unchanged)
        cols_to_show = [
            "Year", "Storage (TB)", "Data to Archive (TB)",
            "Emissions w/o Archival (kg)", "Emissions After Archival (kg)", 
            "Water Savings (L)", "Cost Savings (€)", "Meets Target"
        ]
        display_df = archival_df.copy()
        display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
        formatted_df = display_df[cols_to_show].style.format({
            "Storage (TB)": "{:.2f}", "Data to Archive (TB)": "{:.2f}",
            "Emissions w/o Archival (kg)": "{:,.0f}", "Emissions After Archival (kg)": "{:,.0f}",
            "Water Savings (L)": "{:,.0f}", "Cost Savings (€)": "€{:,.0f}"
        })
        st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    
    # 4. DISPLAY FOOTER
    render_footer()

def render_cloud_section():
    run_cloud_optimizer()

def run():
    run_cloud_optimizer()

if __name__ == "__main__":
    run_cloud_optimizer()
