import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ensure the 'cloud' package is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Constants for human-readable metrics
LITERS_PER_SHOWER = 50 

# --- 1. ROBUST IMPORT BLOCK ---
try:
    from cloud.cloud_cal import (
        df_cloud, 
        calculate_annual_emissions, 
        calculate_annual_water, 
        calculate_annual_cost, 
        calculate_archival_needed,
        ARCHIVAL_WATER_REDUCTION,
        OLYMPIC_POOL_LITERS,
        CO2_PER_TREE_PER_YEAR
    )
except ImportError:
    try:
        from cloud import (
            df_cloud, 
            calculate_annual_emissions, 
            calculate_annual_water, 
            calculate_annual_cost, 
            calculate_archival_needed,
            ARCHIVAL_WATER_REDUCTION,
            OLYMPIC_POOL_LITERS,
            CO2_PER_TREE_PER_YEAR
        )
    except ImportError:
        st.error("Missing components. Please ensure the 'cloud' folder contains '__init__.py'.")
        st.stop()

# --- GLOBAL PAGE CONFIG ---
st.set_page_config(
    page_title="Green IT Decision Portal",
    page_icon="🌱",
    layout="wide"
)

# Custom Metric Helper to allow small sub-text within the "Square"
def render_metric_card(label, value, equivalent_text, equivalent_emoji, help_text=""):
    st.markdown(f"""
        <div class="custom-metric">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-equivalent">{equivalent_emoji} ~{equivalent_text}</div>
        </div>
    """, unsafe_allow_html=True)

# Shared CSS for consistent display
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* CUSTOM METRIC SQUARE STYLING */
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

    /* URGENT RED ALERT BOX */
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
        line-1.5;
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


# --- NEW VISUALIZATION FUNCTIONS ---

def create_diverging_path_chart(archival_df, reduction_target):
    """PRIMARY VISUALIZATION: Shows the widening gap between action and inaction."""
    fig = go.Figure()
    
    # Line for Business As Usual (destructive path)
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions w/o Archival (kg)'],
        name='Without Action',
        line=dict(color='#ef4444', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='x'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    # Line for Optimized path
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions After Archival (kg)'],
        name='With Strategic Archival',
        line=dict(color='#10b981', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    # Fill the GAP between them
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
    
    # Add annotation for total gap
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
    
    # Add reduction target line
    first_year_baseline = archival_df['Emissions w/o Archival (kg)'].iloc[0]
    target_line = first_year_baseline * (1 - reduction_target/100)
    
    fig.add_hline(
        y=target_line,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=3,
        annotation_text=f"Target: {reduction_target}% Reduction",
        annotation_position="right",
        annotation_font_size=13,
        annotation_font_color="#92400e"
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


def create_waterfall_savings_chart(archival_df):
    """SECONDARY VISUALIZATION: Shows cumulative ROI buildup year by year."""
    yearly_savings = archival_df['Cost Savings (€)'].values
    years = [f"Year {y}" for y in archival_df['Year']]
    
    fig = go.Figure(go.Waterfall(
        name="Cost Savings",
        orientation="v",
        measure=["relative"] * len(yearly_savings) + ["total"],
        x=years + ["Total ROI"],
        textposition="outside",
        text=[f"€{val:,.0f}" for val in yearly_savings] + [f"€{yearly_savings.sum():,.0f}"],
        y=list(yearly_savings) + [yearly_savings.sum()],
        connector={"line": {"color": "#64748b", "width": 2, "dash": "dot"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#0ea5e9", "line": {"color": "#0369a1", "width": 3}}}
    ))
    
    fig.update_layout(
        title={
            'text': '<b>Cumulative Financial ROI Over Time</b><br><sub>Each year compounds your savings</sub>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>Cost Savings (€)</b>",
        height=450,
        template='plotly_white',
        showlegend=False,
        plot_bgcolor='#f8fafc',
        paper_bgcolor='white'
    )
    
    return fig


def create_gauge_chart(current_value, target_value, max_value, title, unit):
    """BONUS: Gauge chart for showing progress toward target."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=target_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b><br><sub>{unit}</sub>", 'font': {'size': 16}},
        delta={'reference': current_value, 'increasing': {'color': "#ef4444"}, 
               'decreasing': {'color': "#10b981"}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': "#10b981", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#cbd5e1",
            'steps': [
                {'range': [0, target_value], 'color': '#dcfce7'},
                {'range': [target_value, current_value], 'color': '#fef2f2'}
            ],
            'threshold': {
                'line': {'color': "#f59e0b", 'width': 4},
                'thickness': 0.75,
                'value': target_value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='white',
        font={'color': "#1e293b"}
    )
    
    return fig


def create_multi_metric_comparison(archival_df, current_emissions, current_water, 
                                   liters_per_shower, co2_per_tree):
    """TERTIARY VISUALIZATION: Side-by-side Year 1 vs Final Year comparison."""
    year_1 = archival_df.iloc[0]
    year_final = archival_df.iloc[-1]
    final_year_num = archival_df['Year'].iloc[-1]
    
    final_emissions_optimized = year_final['Emissions After Archival (kg)']
    final_emissions_bau = year_final['Emissions w/o Archival (kg)']
    final_water_optimized = year_final['Water After Archival (L)']
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            f'<b>CO₂ Emissions</b><br><sub>(kg per year)</sub>',
            f'<b>Water Usage</b><br><sub>(Liters per year)</sub>',
            f'<b>Trees Equivalent</b><br><sub>(Annual offset needed)</sub>'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    # CO2 Comparison
    fig.add_trace(
        go.Bar(
            x=['Year 1<br>No Action', f'Year {final_year_num}<br>No Action', 
               'Year 1<br>Optimized', f'Year {final_year_num}<br>Optimized'],
            y=[current_emissions, final_emissions_bau, 
               year_1['Emissions After Archival (kg)'], final_emissions_optimized],
            marker_color=['#fca5a5', '#7f1d1d', '#86efac', '#15803d'],
            text=[f"{current_emissions:,.0f}", f"{final_emissions_bau:,.0f}",
                  f"{year_1['Emissions After Archival (kg)']:,.0f}", 
                  f"{final_emissions_optimized:,.0f}"],
            textposition='outside',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Water Comparison
    fig.add_trace(
        go.Bar(
            x=['Year 1<br>Wasteful', f'Year {final_year_num}<br>Wasteful',
               'Year 1<br>Efficient', f'Year {final_year_num}<br>Efficient'],
            y=[current_water, year_final['Water w/o Archival (L)'],
               year_1['Water After Archival (L)'], final_water_optimized],
            marker_color=['#93c5fd', '#1e3a8a', '#7dd3fc', '#0369a1'],
            text=[f"{current_water/1000:.0f}k", f"{year_final['Water w/o Archival (L)']/1000:.0f}k",
                  f"{year_1['Water After Archival (L)']/1000:.0f}k", 
                  f"{final_water_optimized/1000:.0f}k"],
            textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Trees Comparison
    trees_y1_bau = current_emissions / co2_per_tree
    trees_final_bau = final_emissions_bau / co2_per_tree
    trees_y1_opt = year_1['Emissions After Archival (kg)'] / co2_per_tree
    trees_final_opt = final_emissions_optimized / co2_per_tree
    
    fig.add_trace(
        go.Bar(
            x=['Year 1<br>Needed', f'Year {final_year_num}<br>Needed',
               'Year 1<br>Needed', f'Year {final_year_num}<br>Needed'],
            y=[trees_y1_bau, trees_final_bau, trees_y1_opt, trees_final_opt],
            marker_color=['#fca5a5', '#7f1d1d', '#86efac', '#15803d'],
            text=[f"{trees_y1_bau:,.0f}", f"{trees_final_bau:,.0f}",
                  f"{trees_y1_opt:,.0f}", f"{trees_final_opt:,.0f}"],
            textposition='outside',
            showlegend=False
        ),
        row=1, col=3
    )
    
    fig.update_layout(
        title={
            'text': f'<b>Trajectory Comparison: Year 1 → Year {final_year_num}</b><br><sub>Watch metrics diverge without intervention</sub>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        height=400,
        template='plotly_white',
        showlegend=False,
        plot_bgcolor='#f8fafc',
        paper_bgcolor='white'
    )
    
    fig.update_yaxes(title_text="kg CO₂", row=1, col=1)
    fig.update_yaxes(title_text="Liters", row=1, col=2)
    fig.update_yaxes(title_text="Trees", row=1, col=3)
    
    return fig


def run_cloud_optimizer():
    """Function to render the Cloud Optimizer page."""
    st.title("Cloud Storage Sustainability Advisor")
    st.write("Optimize your data center footprint through intelligent archival strategies.")

    # --- INPUTS ---
    st.subheader("Settings")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        selected_providers = st.multiselect("Cloud Providers", options=df_cloud['Provider'].unique().tolist(), default=["AWS"])
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c3:
        reduction_target = st.slider("CO₂ Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.number_input("Projection Period (Years)", 1, 10, 5)
    with c5:
        data_growth_rate = st.slider("Data Growth Rate (%/year)", 0, 50, 15)

    # Calculation Prep
    storage_gb = storage_tb * 1024
    
    # Calculate Blended Intensity for selected providers
    filtered = df_cloud[df_cloud['Provider'].isin(selected_providers if selected_providers else ["AWS"])]
    std_co2 = filtered['CO2_kg_TB_Month'].iloc[0] if not filtered.empty else 6.0
    carbon_intensity = (std_co2 * 12 / (1024 * 1.2)) * 1000
    
    current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
    current_water_liters = calculate_annual_water(storage_gb)
    target_emissions_kg = current_emissions * (1 - reduction_target / 100)

    # Convert Water to Showers and CO2 to Trees
    current_showers = current_water_liters / LITERS_PER_SHOWER
    current_trees = current_emissions / CO2_PER_TREE_PER_YEAR

    # --- ANNUAL SNAPSHOT (DIAGNOSTIC) ---
    st.divider()
    st.subheader("Current Annual Baseline")
    st.caption("These metrics show your current yearly impact before optimization.")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card("Annual Carbon Footprint", f"{current_emissions:,.0f} kg CO₂", f"{current_trees:,.0f} Trees", "🌳")
    with m2:
        render_metric_card("Annual Water Usage", f"{current_water_liters:,.0f} Liters", f"{current_showers:,.0f} Showers", "🚿")
    with m3:
        st.markdown(f"""<div class="custom-metric">
            <div class="metric-label">Yearly Goal Target</div>
            <div class="metric-value" style="color: #059669;">{target_emissions_kg:,.0f} kg CO₂</div>
            <div class="metric-equivalent">🎯 Required {reduction_target}% reduction</div>
        </div>""", unsafe_allow_html=True)

    # --- STRATEGY ---
    st.subheader("🚨 ACTION REQUIRED IMMEDIATELY")
    
    # Run the math engine
    archival_df = calculate_archival_needed(
        storage_gb, target_emissions_kg, carbon_intensity, projection_years, 
        data_growth_rate / 100, 0.90, 0.022, 0.004 
    )
    
    year_1 = archival_df.iloc[0]
    
    # Urgent Disclaimer Card
    st.markdown(f"""
    <div class="urgent-alert">
        <h3>Immediate Intervention Required</h3>
        <p><b>CRITICAL:</b> To halt your current environmental debt, you must archive <b>{year_1['Data to Archive (TB)']:.1f} TB</b> 
        of data immediately. Doing nothing will cause your emissions to surge exponentially as your data grows. 
        Moving to Cold Storage is no longer a choice—it is a requirement to hit your <b>{reduction_target}%</b> reduction mandate.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- CUMULATIVE IMPACT ---
    st.subheader(f"📈 Total {projection_years}-Year Environmental Gap")
    
    total_co2_no_action = archival_df["Emissions w/o Archival (kg)"].sum()
    total_co2_optimized = archival_df["Emissions After Archival (kg)"].sum()
    total_savings_co2 = total_co2_no_action - total_co2_optimized
    total_savings_euro = archival_df["Cost Savings (€)"].sum()
    total_water_saved_liters = archival_df["Water Savings (L)"].sum()
    
    total_showers_saved = total_water_saved_liters / LITERS_PER_SHOWER
    total_trees_equivalent = total_savings_co2 / CO2_PER_TREE_PER_YEAR

    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card("Total CO₂ Saved", f"{total_savings_co2:,.0f} kg CO₂", f"{total_trees_equivalent:,.0f} Trees", "🌳")
    with k2:
        render_metric_card("Total Water Reclaimed", f"{total_water_saved_liters:,.0f} Liters", f"{total_showers_saved:,.0f} Showers", "🚿")
    with k3:
        st.markdown(f"""<div class="custom-metric">
            <div class="metric-label">Total Financial ROI</div>
            <div class="metric-value">€{total_savings_euro:,.0f}</div>
            <div class="metric-equivalent">💰 Avoided Costs over {projection_years}y</div>
        </div>""", unsafe_allow_html=True)

    # --- NEW VISUALIZATIONS SECTION (REPLACES OLD CHARTS) ---
    st.write("### 📊 Visual Impact Analysis")
    st.caption("Diverging path visualization showing the magnitude and urgency of action")

    # PRIMARY: Diverging Path Chart ONLY
    st.plotly_chart(
        create_diverging_path_chart(archival_df, reduction_target),
        use_container_width=True,
        key="diverging_path"
    )

    # --- TECHNICAL BREAKDOWN ---
    with st.expander("🧬 View Technical Breakdown & Data Evolution"):
        st.write("Detailed annualized metrics showing storage growth and archival targets.")
        
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
    
    # --- METHODOLOGY SECTION (AT THE END OF PAGE) ---
    st.divider()
    st.write("**Methodology & Calculation Logic**")
    st.write(f"""
        - 💨 **Carbon Intensity:** Calculated at {carbon_intensity:.0f} gCO₂/kWh based on cloud region energy mix.
        - 🚿 **Water Equivalency:** 1 Shower is standardized at **{LITERS_PER_SHOWER} Liters** (Average duration and flow rate).
        - 🌳 **Tree Equivalency:** 1 Mature tree offsets **{CO2_PER_TREE_PER_YEAR} kg CO₂** per year (Winrock/One Tree Planted).
        - 📦 **Urgency Logic:** Delaying archival for even one year increases the 'Recovery TB' needed by {data_growth_rate}% due to data growth compounding.
    """)

# Main entry
if __name__ == "__main__":
    st.title("Green IT Lifecycle & ROI Optimization")
    st.markdown("### Strategic decision-making models for a sustainable circular economy.")
    
    st.divider()
    run_cloud_optimizer()
