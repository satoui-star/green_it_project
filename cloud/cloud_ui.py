import streamlit as st
import plotly.graph_objects as go
import os
import base64

from cloud_cal import (
    get_cloud_providers,
    calculate_carbon_intensity,
    calculate_baseline_metrics,
    calculate_archival_strategy,
    calculate_cumulative_savings,
    LITERS_PER_SHOWER,
    CO2_PER_TREE_PER_YEAR
)

st.set_page_config(
    page_title="Green IT Decision Portal",
    layout="wide"
)

# === LOGO & HEADER LOGIC ===
def render_logo():
    """Render the Elysia logo image with a fallback to text."""
    logo_path = "logo.png/elysia_logo.png" 

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        st.markdown(f"""
        <div class="logo-section">
            <img src="data:image/png;base64,{encoded}" alt="Elysia Logo" style="width: 280px; max-width: 100%; margin-bottom: 10px;">
            <div class="logo-tagline">Where insight drives impact</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="logo-section">
            <div style="font-family: 'Playfair Display', serif; font-size: 60px; color: #8a6c4a; letter-spacing: 8px; margin-bottom: 0px;">ELYSIA</div>
            <div class="logo-tagline">Where insight drives impact</div>
        </div>
        """, unsafe_allow_html=True)

def render_welcome_section():
    """Hard-coded Hero section"""
    st.markdown(f"""
    <div class="welcome-hero">
        <h1 class="welcome-title" style="font-size: 3rem !important; margin-bottom: 20px !important;">Welcome to Élysia</h1>
        <p class="welcome-subtitle" style="text-align: center; margin: 0 auto; max-width: 700px; font-family: 'Cormorant Garamond', serif; font-size: 1.3rem;">
            Your strategic command center for measuring, tracking, and optimizing 
            the environmental impact of LVMH's IT infrastructure across all Maisons.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Luxury Footer section"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 40px 0; font-family: 'Montserrat', sans-serif;">
            <div style="font-family: 'Playfair Display', serif; font-size: 1.2rem; color: #2c2c2c; letter-spacing: 4px; text-transform: uppercase;">Élysia</div>
            <div style="color: #8a6c4a; font-size: 0.7rem; letter-spacing: 2px; margin-top: 10px; text-transform: uppercase;">
                LVMH Group IT Sustainability &copy; 2026
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, equivalent_text, equivalent_emoji, help_text=""):
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{equivalent_emoji}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-unit">~{equivalent_text}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    /* === LIGHT LUXURY BASE === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === LOGO SECTION STYLES === */
    .logo-section {
        text-align: center; padding: 40px 0 30px 0;
        border-bottom: 1px solid #e8e4dc; margin-bottom: 35px;
        background: linear-gradient(180deg, #fff 0%, #faf9f7 100%);
    }
    .logo-tagline {
        font-family: 'Montserrat', sans-serif; font-size: 0.7rem;
        letter-spacing: 4px; color: #8a6c4a; text-transform: uppercase;
    }

    /* === WELCOME HERO STYLES === */
    .welcome-hero {
        background: linear-gradient(135deg, #fff 0%, #f8f6f2 50%, #fff 100%);
        border: 1px solid #e8e4dc; border-radius: 8px;
        padding: 60px 50px; text-align: center;
        box-shadow: 0 4px 20px rgba(138, 108, 74, 0.06);
        margin-bottom: 40px;
    }

    /* === COMPLETELY HIDE EXPANDER ARROWS === */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    [data-testid="stExpander"] svg {
        display: none !important;
        visibility: hidden !important;
    }
    
    [data-testid="stExpander"] {
        background: #fff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 6px !important;
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
    
    .kpi-card::before {
        content: ''; position: absolute; top: 0; left: 50%;
        transform: translateX(-50%); width: 50px; height: 3px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 3px 3px;
    }
    
    .kpi-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.8rem; font-weight: 500; color: #2c2c2c;
    }
    
    /* === URGENT ALERT RECTANGLE === */
    .urgent-alert {
        background: #fef2f2;
        padding: 30px;
        border-radius: 10px;
        border: 2px solid #ef4444; 
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.1);
        margin: 25px 0;
    }

    .urgent-alert-header {
        color: #991b1b; margin-bottom: 15px;
        text-transform: uppercase; letter-spacing: 1.5px;
        font-weight: 700; font-family: 'Montserrat', sans-serif !important;
        font-size: 0.9rem;
    }
    
    /* === DIVIDERS === */
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #d4cfc5, transparent);
        margin: 50px 0;
    }
    
    /* === BUTTONS === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        border-radius: 6px !important;
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
        arrowhead=2, ax=-80, ay=-40,
        font=dict(size=14, color="#991b1b", family="Arial Black"),
        bgcolor="rgba(254, 242, 242, 0.95)",
        bordercolor="#ef4444", borderwidth=2, borderpad=8
    )
    
    fig.update_layout(
        title={'text': '<b>The Diverging Paths: Action vs Inaction</b>', 'font': {'size': 20, 'color': '#1e293b'}},
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Annual CO₂ Emissions (kg)</b>",
        height=550, template='plotly_white',
        plot_bgcolor='#f8fafc', paper_bgcolor='white'
    )
    
    return fig

def run_cloud_optimizer():
    # --- TOP HEADER COMPONENTS ---
    render_logo()
    render_welcome_section()

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
    st.markdown("<br>", unsafe_allow_html=True)
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

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    archival_df = calculate_archival_strategy(storage_gb, reduction_target, data_growth_rate, carbon_intensity, projection_years)
    year_1 = archival_df.iloc[0]
    
    st.markdown(f"""
    <div class="urgent-alert">
        <div class="urgent-alert-header">🚨 Action Required Immediately</div>
        <h3>Immediate Intervention Required</h3>
        <p><b>CRITICAL:</b> Your emissions are directly tied to data growth. To maintain a sustainable <b>{reduction_target}%</b> efficiency gain, you must archive <b>{year_1['Data to Archive (TB)']:.1f} TB</b> 
        this year. In the table below, notice how <b>Emissions After Archival</b> now scale with your business growth, ensuring that your 'Hot' tier remains optimized rather than artificially capped.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader(f"Total {projection_years}-Year Environmental Gap")
    
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
    st.plotly_chart(create_diverging_path_chart(archival_df, reduction_target), width='stretch', key="diverging_path")

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("📊 View Technical Breakdown & Data Evolution"):
        cols_to_show = ["Year", "Storage (TB)", "Data to Archive (TB)", "Emissions w/o Archival (kg)", "Emissions After Archival (kg)", "Water Savings (L)", "Cost Savings (€)"]
        display_df = archival_df.copy()
        display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
        formatted_df = display_df[cols_to_show].style.format({"Storage (TB)": "{:.2f}", "Data to Archive (TB)": "{:.2f}", "Emissions w/o Archival (kg)": "{:,.0f}", "Emissions After Archival (kg)": "{:,.0f}", "Water Savings (L)": "{:,.0f}", "Cost Savings (€)": "€{:,.0f}"})
        st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    
    # --- FOOTER ---
    render_footer()

if __name__ == "__main__":
    run_cloud_optimizer()
