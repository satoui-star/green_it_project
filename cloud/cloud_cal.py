import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def create_diverging_path_chart(archival_df, reduction_target):
    """
    PRIMARY VISUALIZATION: Shows the widening gap between action and inaction.
    This is the most powerful chart for demonstrating urgency.
    """
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
    
    # Fill the GAP between them - this is the visual "waste"
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
    """
    SECONDARY VISUALIZATION: Shows cumulative ROI buildup year by year.
    Makes the financial case immediately clear.
    """
    # Calculate incremental savings per year
    yearly_savings = archival_df['Cost Savings (€)'].values
    
    # Waterfall chart data
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


def create_multi_metric_comparison(archival_df, current_emissions, current_water, 
                                   liters_per_shower, co2_per_tree):
    """
    TERTIARY VISUALIZATION: Side-by-side Year 1 vs Final Year comparison.
    Shows the trajectory across all three metrics simultaneously.
    """
    year_1 = archival_df.iloc[0]
    year_final = archival_df.iloc[-1]
    final_year_num = archival_df['Year'].iloc[-1]
    
    # Calculate final year values
    final_emissions_optimized = year_final['Emissions After Archival (kg)']
    final_emissions_bau = year_final['Emissions w/o Archival (kg)']
    final_water_optimized = year_final['Water After Archival (L)']
    
    # Create subplots
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
    
    # Update y-axes
    fig.update_yaxes(title_text="kg CO₂", row=1, col=1)
    fig.update_yaxes(title_text="Liters", row=1, col=2)
    fig.update_yaxes(title_text="Trees", row=1, col=3)
    
    return fig


def create_gauge_chart(current_value, target_value, max_value, title, unit):
    """
    BONUS: Gauge chart for showing progress toward target.
    """
    reduction_pct = ((current_value - target_value) / current_value) * 100
    
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


# INTEGRATION EXAMPLE - Replace your existing plotting section with:
"""
# --- REPLACE YOUR EXISTING "The Impact Contrast" SECTION WITH THIS ---

st.write("### 📊 Visual Impact Analysis")
st.caption("Three complementary views showing the magnitude and urgency of action")

# PRIMARY: Diverging Path Chart
st.plotly_chart(
    create_diverging_path_chart(archival_df, reduction_target),
    use_container_width=True,
    key="diverging_path"
)

col_left, col_right = st.columns(2)

with col_left:
    # SECONDARY: Waterfall ROI
    st.plotly_chart(
        create_waterfall_savings_chart(archival_df),
        use_container_width=True,
        key="waterfall"
    )

with col_right:
    # BONUS: Gauge for Year 1 target
    st.plotly_chart(
        create_gauge_chart(
            current_emissions, 
            target_emissions_kg,
            current_emissions * 1.2,
            "Year 1 Target Achievement",
            "kg CO₂"
        ),
        use_container_width=True,
        key="gauge_y1"
    )

# TERTIARY: Multi-metric trajectory
st.plotly_chart(
    create_multi_metric_comparison(
        archival_df, 
        current_emissions, 
        current_water_liters,
        LITERS_PER_SHOWER,
        CO2_PER_TREE_PER_YEAR
    ),
    use_container_width=True,
    key="multi_metric"
)

# --- REMOVE your old area chart entirely ---
"""
