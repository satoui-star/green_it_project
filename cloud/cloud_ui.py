import streamlit as st
import plotly.graph_objects as go
from cloud/cloud_cal import (
    get_cloud_providers,
    calculate_carbon_intensity,
    calculate_baseline_metrics,
    calculate_archival_strategy,
    calculate_cumulative_savings,
    LITERS_PER_SHOWER,
    CO2_PER_TREE_PER_YEAR
)

st.set_page_config(
    page_title="Elysia Cloud Solution",
    page_icon="",
    layout="wide"
)

def render_metric_card(label, value, equivalent_text, equivalent_emoji, help_text=""):
    st.markdown(f"""
        <div class="custom-metric">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-equivalent">{equivalent_emoji} ~{equivalent_text}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    .custom-metric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-equivalent {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        margin-top: 6px;
    }

    .urgent-alert {
        background-color: #fef2f2;
        padding: 28px;
        border-radius: 16px;
        border: 2px solid #ef4444;
        border-left: 12px solid #ef4444;
        box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.1);
        margin-bottom: 30px;
    }
    .urgent-alert h3 {
        color: #991b1b;
        margin-top: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 800;
    }
    .urgent-alert p {
        color: #7f1d1d;
        font-size: 1.1rem;
        line-height: 1.5;
    }
    
    .status-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .status-ok { background-color: #dcfce7; color: #15803d; }
    .status-risk { background-color: #fee2e2; color: #b91c1c; }
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

def render_cloud_section():
    st.markdown("### ☁️ Cloud Storage Optimizer")
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
        data_growth_rate = st.slider("Data Growth Rate (%/year)", 0, 50, 15)
    with c5:
        projection_years = st.number_input("Projection Period (Years)", 1, 10, 5)

    storage_gb = storage_tb * 1024
    carbon_intensity = calculate_carbon_intensity(selected_providers)
    baseline = calculate_baseline_metrics(storage_gb, carbon_intensity)

    st.divider()
    st.subheader("Current Annual Baseline")
    st.caption("These metrics show your current yearly impact before optimization.")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card("Annual Carbon Footprint", f"{baseline['emissions']:,.0f} kg CO₂", f"{baseline['trees']:,.0f} Trees", "🌳")
    with m2:
        render_metric_card("Annual Water Usage", f"{baseline['water_liters']:,.0f} Liters", f"{baseline['showers']:,.0f} Showers", "🚿")
    with m3:
        st.markdown(f"""<div class="custom-metric">
            <div class="metric-label">Efficiency Goal</div>
            <div class="metric-value" style="color: #059669;">-{reduction_target}%</div>
            <div class="metric-equivalent">🎯 Relative reduction vs growth</div>
        </div>""", unsafe_allow_html=True)

    st.subheader("🚨 ACTION REQUIRED IMMEDIATELY")
    
    archival_df = calculate_archival_strategy(storage_gb, reduction_target, data_growth_rate, carbon_intensity, projection_years)
    year_1 = archival_df.iloc[0]
    
    st.markdown(f"""
    <div class="urgent-alert">
        <h3>Immediate Intervention Required</h3>
        <p><b>CRITICAL:</b> Your emissions are directly tied to data growth. To maintain a sustainable <b>{reduction_target}%</b> efficiency gain, you must archive <b>{year_1['Data to Archive (TB)']:.1f} TB</b> 
        this year. In the table below, notice how <b>Emissions After Archival</b> now scale with your business growth, ensuring that your 'Hot' tier remains optimized rather than artificially capped.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader(f"Total {projection_years}-Year Environmental Gap")
    
    cumulative = calculate_cumulative_savings(archival_df)

    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card("Total CO₂ Saved", f"{cumulative['co2_saved']:,.0f} kg CO₂", f"{cumulative['trees_equivalent']:,.0f} Trees", "🌳")
    with k2:
        render_metric_card("Total Water Reclaimed", f"{cumulative['water_saved']:,.0f} Liters", f"{cumulative['showers_saved']:,.0f} Showers", "🚿")
    with k3:
        st.markdown(f"""<div class="custom-metric">
            <div class="metric-label">Total Financial ROI</div>
            <div class="metric-value">€{cumulative['euro_saved']:,.0f}</div>
            <div class="metric-equivalent">💰 Avoided Costs over {projection_years}y</div>
        </div>""", unsafe_allow_html=True)

    st.write("### Visual Impact Analysis")
    st.caption("Diverging path visualization showing the magnitude and urgency of action")

    st.plotly_chart(
        create_diverging_path_chart(archival_df, reduction_target),
        use_container_width=True,
        key="diverging_path"
    )

    with st.expander("🧬 View Technical Breakdown & Data Evolution"):
        st.write("Detailed annualized metrics. Note how 'Emissions After Archival' increases relative to data growth, acknowledging business scaling.")
        
        cols_to_show = [
            "Year", "Storage (TB)", "Data to Archive (TB)",
            "Emissions w/o Archival (kg)", "Emissions After Archival (kg)", 
            "Water Savings (L)", "Cost Savings (€)", "Meets Target"
        ]
        
        display_df = archival_df.copy()
        display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
        
        formatted_df = display_df[cols_to_show].style.format({
            "Storage (TB)": "{:.2f}",
            "Data to Archive (TB)": "{:.2f}",
            "Emissions w/o Archival (kg)": "{:,.0f}",
            "Emissions After Archival (kg)": "{:,.0f}",
            "Water Savings (L)": "{:,.0f}",
            "Cost Savings (€)": "€{:,.0f}"
        })
        
        st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    
    st.divider()
    st.write("**Methodology & Calculation Logic**")
    st.write(f"""
        - **Carbon Intensity:** Calculated at {carbon_intensity:.0f} gCO₂/kWh based on cloud region energy mix.
        - **Water Equivalency:** 1 Shower is standardized at **{LITERS_PER_SHOWER} Liters** (Average duration and flow rate).
        - **Tree Equivalency:** 1 Mature tree offsets **{CO2_PER_TREE_PER_YEAR} kg CO₂** per year (Winrock/One Tree Planted).
        - **Dynamic Scaling:** Unlike a static carbon cap, this model applies the reduction target to each year's projected growth. This means 'Emissions After Archival' grows at a sustainable rate rather than staying constant.
    """)

def run():
    render_cloud_section()

if __name__ == "__main__":
    st.title("Élysia Cloud Solution")
    st.markdown("### Strategic decision-making model for a sustainable cloud storage.")
    
    st.divider()
    render_cloud_section()
