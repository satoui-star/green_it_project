"""
Élysia - Credibility UI Components
===================================
LVMH · Sustainable IT Intelligence

Streamlit components for displaying:
- Confidence badges
- Source citations
- Disclaimers
- Methodology explanations
- Range displays instead of point estimates
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple


# =============================================================================
# CSS FOR CREDIBILITY COMPONENTS
# =============================================================================

CREDIBILITY_CSS = """
<style>
/* Confidence Badges */
.confidence-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-left: 8px;
}

.confidence-high {
    background: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #A5D6A7;
}

.confidence-medium {
    background: #FFF8E1;
    color: #F57F17;
    border: 1px solid #FFE082;
}

.confidence-low {
    background: #FFEBEE;
    color: #C62828;
    border: 1px solid #EF9A9A;
}

.confidence-theoretical {
    background: #F5F5F5;
    color: #616161;
    border: 1px solid #BDBDBD;
}

/* Disclaimer Box */
.disclaimer-box {
    background: #FFFBF0;
    border: 1px solid #FFE082;
    border-left: 4px solid #FFA000;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #5D4037;
}

.disclaimer-box-title {
    font-weight: 600;
    color: #E65100;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.disclaimer-box-text {
    line-height: 1.6;
}

/* Source Citation */
.source-citation {
    background: #F5F5F5;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #616161;
}

.source-citation-label {
    font-weight: 600;
    color: #424242;
}

/* Range Display */
.range-display {
    background: linear-gradient(90deg, #FFEBEE 0%, #FFF8E1 50%, #E8F5E9 100%);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    text-align: center;
}

.range-values {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.5rem;
}

.range-low {
    color: #C62828;
    font-size: 0.9rem;
}

.range-mid {
    font-weight: 700;
    font-size: 1.25rem;
    color: #424242;
}

.range-high {
    color: #2E7D32;
    font-size: 0.9rem;
}

/* Methodology Card */
.methodology-card {
    background: white;
    border: 1px solid #E8E4DD;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.methodology-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.1rem;
    color: #2D2A26;
    margin-bottom: 0.75rem;
}

.methodology-formula {
    font-family: 'Monaco', 'Consolas', monospace;
    background: #F5F5F5;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    color: #1565C0;
    margin: 0.5rem 0;
}

.methodology-limitations {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #E8E4DD;
}

.limitation-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: #616161;
}

.limitation-icon {
    color: #FFA000;
}

/* Info Tooltip */
.info-tooltip {
    display: inline-block;
    width: 16px;
    height: 16px;
    background: #E0E0E0;
    color: #616161;
    border-radius: 50%;
    text-align: center;
    font-size: 0.7rem;
    line-height: 16px;
    cursor: help;
    margin-left: 4px;
}
</style>
"""


# =============================================================================
# CONFIDENCE BADGE COMPONENT
# =============================================================================

def render_confidence_badge(confidence: str) -> str:
    """
    Render a confidence level badge.
    
    Args:
        confidence: "HIGH", "MEDIUM", "LOW", or "THEORETICAL"
    
    Returns:
        HTML string for the badge
    """
    confidence_class = {
        "HIGH": "confidence-high",
        "MEDIUM": "confidence-medium",
        "LOW": "confidence-low",
        "THEORETICAL": "confidence-theoretical",
    }.get(confidence.upper(), "confidence-medium")
    
    return f'<span class="confidence-badge {confidence_class}">{confidence}</span>'


def confidence_badge(confidence: str, inline: bool = True):
    """Streamlit component for confidence badge."""
    html = render_confidence_badge(confidence)
    if inline:
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(f"<div>{html}</div>", unsafe_allow_html=True)


# =============================================================================
# DISCLAIMER BOX COMPONENT
# =============================================================================

def render_disclaimer(title: str, text: str, icon: str = "⚠️") -> str:
    """Render a disclaimer box."""
    return f"""
    <div class="disclaimer-box">
        <div class="disclaimer-box-title">{icon} {title}</div>
        <div class="disclaimer-box-text">{text}</div>
    </div>
    """


def disclaimer_box(title: str, text: str, icon: str = "⚠️"):
    """Streamlit component for disclaimer box."""
    st.markdown(render_disclaimer(title, text, icon), unsafe_allow_html=True)


# Standard disclaimers
def show_general_disclaimer():
    """Show the general methodology disclaimer."""
    disclaimer_box(
        "Important",
        "Élysia provides estimates based on industry benchmarks and publicly available data. "
        "Actual results may vary based on your specific circumstances, market conditions, and "
        "implementation approach. Use these projections for directional planning, not as precise "
        "financial forecasts."
    )


def show_stranded_value_disclaimer():
    """Show disclaimer for stranded value metric."""
    disclaimer_box(
        "About This Metric",
        "Stranded value represents the <em>theoretical</em> residual value based on standard "
        "depreciation curves. In practice, recoverable value depends on your resale strategy, "
        "data security requirements, and market conditions. Many enterprises don't resell devices, "
        "making actual recoverable value €0. <strong>Use as directional indicator only.</strong>"
    )


def show_productivity_disclaimer():
    """Show disclaimer for productivity estimates."""
    disclaimer_box(
        "Theoretical Estimate",
        "Productivity loss calculations are based on industry research (Gartner Digital Workplace "
        "Study 2023) but are inherently difficult to measure precisely. The actual impact depends "
        "on specific work tasks, user behavior, and IT support quality. "
        "<strong>Consider these figures as illustrative rather than precise.</strong>"
    )


def show_refurbished_disclaimer():
    """Show disclaimer for refurbished assumptions."""
    disclaimer_box(
        "Availability Note",
        "Refurbished device availability, pricing, and quality vary significantly by model, "
        "region, and supplier. The 80% CO₂ savings figure is based on Dell's Circular Economy "
        "Report. Enterprise-grade supply at scale may be limited for specific models. "
        "<strong>Verify availability with suppliers before committing to targets.</strong>"
    )


# =============================================================================
# SOURCE CITATION COMPONENT
# =============================================================================

def render_source(source: str, url: Optional[str] = None, confidence: Optional[str] = None) -> str:
    """Render a source citation."""
    link = f'<a href="{url}" target="_blank">{source}</a>' if url else source
    badge = render_confidence_badge(confidence) if confidence else ""
    return f"""
    <div class="source-citation">
        <span class="source-citation-label">Source:</span> {link} {badge}
    </div>
    """


def source_citation(source: str, url: Optional[str] = None, confidence: Optional[str] = None):
    """Streamlit component for source citation."""
    st.markdown(render_source(source, url, confidence), unsafe_allow_html=True)


# =============================================================================
# RANGE DISPLAY COMPONENT
# =============================================================================

def render_range(low: float, mid: float, high: float, 
                 unit: str = "", label: str = "", fmt: str = ",.0f") -> str:
    """
    Render a value range instead of a single point estimate.
    
    Args:
        low: Conservative estimate
        mid: Best estimate
        high: Optimistic estimate
        unit: Unit string (e.g., "€", "t CO₂")
        label: Label for the metric
        fmt: Format string for numbers
    """
    return f"""
    <div class="range-display">
        <div style="font-size: 0.8rem; color: #616161; margin-bottom: 0.5rem;">{label}</div>
        <div class="range-values">
            <div class="range-low">Low<br><strong>{unit}{low:{fmt}}</strong></div>
            <div class="range-mid">{unit}{mid:{fmt}}</div>
            <div class="range-high">High<br><strong>{unit}{high:{fmt}}</strong></div>
        </div>
        <div style="font-size: 0.7rem; color: #9E9E9E; margin-top: 0.5rem;">
            Range reflects uncertainty in assumptions
        </div>
    </div>
    """


def range_display(low: float, mid: float, high: float,
                  unit: str = "", label: str = "", fmt: str = ",.0f"):
    """Streamlit component for range display."""
    st.markdown(render_range(low, mid, high, unit, label, fmt), unsafe_allow_html=True)


def metric_with_range(label: str, value: float, low: float, high: float,
                      unit: str = "", confidence: str = "MEDIUM"):
    """
    Display a metric with its uncertainty range.
    
    Better than st.metric() because it shows the range.
    """
    badge = render_confidence_badge(confidence)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 0.8rem; color: #6B6560;">{label} {badge}</div>
        <div style="font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 500; color: #2D2A26;">
            {unit}{value:,.0f}
        </div>
        <div style="font-size: 0.75rem; color: #9E9E9E;">
            Range: {unit}{low:,.0f} – {unit}{high:,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# METHODOLOGY CARD COMPONENT
# =============================================================================

def methodology_card(title: str, formula: str, description: str,
                     limitations: List[str], confidence: str,
                     validation_status: str = "Not validated"):
    """
    Display a methodology explanation card.
    
    Use in a "Methodology" tab or expander.
    """
    limitations_html = "".join([
        f'<div class="limitation-item"><span class="limitation-icon">⚠️</span> {lim}</div>'
        for lim in limitations
    ])
    
    badge = render_confidence_badge(confidence)
    
    st.markdown(f"""
    <div class="methodology-card">
        <div class="methodology-title">{title} {badge}</div>
        <p style="color: #616161; font-size: 0.9rem;">{description}</p>
        <div class="methodology-formula">{formula}</div>
        <div class="methodology-limitations">
            <div style="font-weight: 600; font-size: 0.85rem; color: #424242; margin-bottom: 0.5rem;">
                Limitations & Caveats
            </div>
            {limitations_html}
        </div>
        <div style="margin-top: 1rem; font-size: 0.8rem; color: #9E9E9E;">
            Validation: {validation_status}
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# SOURCES TAB COMPONENT
# =============================================================================

def render_sources_table(sources: Dict[str, Dict]) -> None:
    """
    Render a table of all data sources with confidence levels.
    
    Args:
        sources: Dict from get_all_sources()
    """
    import pandas as pd
    
    data = []
    for category, info in sources.items():
        if isinstance(info, dict):
            data.append({
                "Category": category,
                "Source": info.get("source", "—"),
                "Confidence": info.get("confidence", "—"),
            })
        else:
            data.append({
                "Category": category,
                "Source": str(info),
                "Confidence": "—",
            })
    
    df = pd.DataFrame(data)
    
    # Color code confidence
    def highlight_confidence(val):
        colors = {
            "HIGH": "background-color: #E8F5E9",
            "MEDIUM": "background-color: #FFF8E1",
            "LOW": "background-color: #FFEBEE",
            "THEORETICAL": "background-color: #F5F5F5",
        }
        return colors.get(val, "")
    
    styled = df.style.applymap(highlight_confidence, subset=["Confidence"])
    st.dataframe(styled, use_container_width=True, hide_index=True)


def sources_expander(sources: Dict[str, Dict]):
    """Show sources in an expander."""
    with st.expander("📚 View Data Sources & Confidence Levels"):
        render_sources_table(sources)
        st.markdown("""
        **Confidence Levels:**
        - 🟢 **HIGH**: Official sources, measured data (±10%)
        - 🟡 **MEDIUM**: Industry benchmarks (±25%)
        - 🔴 **LOW**: Estimates, significant uncertainty (±50%)
        - ⚪ **THEORETICAL**: Model-based, not validated (±75%)
        """)


# =============================================================================
# ENHANCED METRIC CARD WITH SOURCES
# =============================================================================

def enhanced_metric_card(
    value: float,
    label: str,
    unit: str = "€",
    confidence: str = "MEDIUM",
    source: str = "",
    formula: str = "",
    range_low: Optional[float] = None,
    range_high: Optional[float] = None,
    caveat: Optional[str] = None,
    color: str = "gold"
):
    """
    Render a metric card with full transparency.
    
    Includes:
    - Main value
    - Confidence badge
    - Optional range
    - Source citation
    - Formula (in expander)
    - Caveat if applicable
    """
    color_map = {
        "gold": "#8a6c4a",
        "success": "#4A7C59",
        "danger": "#9E4A4A",
    }
    value_color = color_map.get(color, "#8a6c4a")
    
    badge = render_confidence_badge(confidence)
    
    range_html = ""
    if range_low is not None and range_high is not None:
        range_html = f"""
        <div style="font-size: 0.8rem; color: #9E9E9E; margin-top: 0.5rem;">
            Range: {unit}{range_low:,.0f} – {unit}{range_high:,.0f}
        </div>
        """
    
    st.markdown(f"""
    <div style="background: white; border: 1px solid #E8E4DD; border-radius: 12px; 
                padding: 1.5rem; text-align: center; margin-bottom: 1rem;">
        <div style="font-size: 0.85rem; color: #6B6560; margin-bottom: 0.5rem;">
            {label} {badge}
        </div>
        <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.75rem; 
                    font-weight: 500; color: {value_color};">
            {unit}{value:,.0f}
        </div>
        {range_html}
        <div style="font-size: 0.7rem; color: #BDBDBD; margin-top: 0.75rem;">
            Source: {source}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if caveat:
        with st.expander("ℹ️ About this metric"):
            st.markdown(caveat)
            if formula:
                st.code(formula, language=None)


# =============================================================================
# METHODOLOGY TAB CONTENT
# =============================================================================

def render_methodology_tab():
    """Render full methodology documentation as a Streamlit tab."""
    st.markdown("### Methodology & Transparency")
    
    st.markdown("""
    Élysia uses a combination of manufacturer data, industry benchmarks, and 
    established calculation methods. This page provides full transparency into 
    our assumptions and limitations.
    """)
    
    # Confidence Legend
    st.markdown("#### Confidence Levels")
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f'{render_confidence_badge("HIGH")} Official sources, ±10%', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'{render_confidence_badge("MEDIUM")} Benchmarks, ±25%', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'{render_confidence_badge("LOW")} Estimates, ±50%', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'{render_confidence_badge("THEORETICAL")} Model-based, ±75%', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key Calculations
    st.markdown("#### Key Calculations")
    
    methodology_card(
        title="Stranded Value",
        formula="Stranded Value = Fleet Size × Avg Price × (0.70)^Age",
        description="Theoretical residual value locked in your fleet based on depreciation.",
        limitations=[
            "Assumes devices CAN be resold (many enterprises don't due to data security)",
            "Bulk resale prices are 30-50% lower than individual resale",
            "Some device categories have zero market demand",
            "Use as directional indicator, not financial projection",
        ],
        confidence="LOW",
        validation_status="Not validated - theoretical model"
    )
    
    methodology_card(
        title="CO₂ Savings (Refurbished)",
        formula="CO₂ Saved = Annual Replacements × Refurb Rate × CO₂/device × 80%",
        description="Carbon emissions avoided by choosing refurbished over new devices.",
        limitations=[
            "80% savings is Dell's claim; Apple claims 85%, Back Market claims 91%",
            "Actual savings depend on specific device and refurbishment process",
            "Does not account for transport emissions from refurb supply chain",
        ],
        confidence="MEDIUM",
        validation_status="Based on manufacturer environmental reports"
    )
    
    methodology_card(
        title="Productivity Loss",
        formula="Loss = Salary × (Age - 3) × 3% × Lag_Sensitivity",
        description="Estimated cost of productivity loss from aging devices.",
        limitations=[
            "⚠️ HIGHLY THEORETICAL - productivity is very difficult to measure",
            "Based on Gartner survey data, not direct measurement",
            "Lag sensitivity multipliers are internal estimates, NOT validated",
            "Actual impact depends on specific work tasks and user behavior",
            "Consider 50% discount for conservative financial planning",
        ],
        confidence="THEORETICAL",
        validation_status="NOT VALIDATED - use as illustrative only"
    )
    
    methodology_card(
        title="TCO Comparison",
        formula="TCO = Purchase/Lifespan + Energy + Productivity Loss + Disposal - Residual",
        description="Total Cost of Ownership comparison across Keep/New/Refurbished scenarios.",
        limitations=[
            "Does not include maintenance/repair costs",
            "Does not account for financing costs or opportunity cost of capital",
            "Productivity component has high uncertainty (see above)",
        ],
        confidence="MEDIUM",
        validation_status="Partially validated against Dell TCO models"
    )
    
    st.markdown("---")
    
    # Recommendations
    st.markdown("#### Recommendations for Use")
    st.markdown("""
    1. **Use ranges, not point estimates** — Always consider the low/mid/high range when making decisions
    2. **Validate with pilots** — Test assumptions with a small fleet subset before scaling
    3. **Discount productivity figures** — For financial planning, consider using 50% of calculated productivity loss
    4. **Update assumptions** — Market prices, grid factors, and refurb availability change over time
    5. **Consult stakeholders** — For significant investments, involve Finance, Procurement, and Sustainability teams
    """)


# =============================================================================
# INJECT CSS
# =============================================================================

def inject_credibility_css():
    """Inject the credibility components CSS. Call once at app start."""
    st.markdown(CREDIBILITY_CSS, unsafe_allow_html=True)