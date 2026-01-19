"""
Élysia - Methodology & Transparency Module
============================================
LVMH · Sustainable IT Intelligence

This module provides full transparency into all calculations,
assumptions, and confidence levels used in Élysia.

IMPORTANT: This file is designed to be displayed to users and auditors.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level for estimates."""
    HIGH = "HIGH"      # Based on measured data or official sources
    MEDIUM = "MEDIUM"  # Industry benchmarks, may vary ±20%
    LOW = "LOW"        # Estimates, may vary ±50%
    THEORETICAL = "THEORETICAL"  # Model-based, not validated


@dataclass
class Assumption:
    """Documents a single assumption."""
    name: str
    value: any
    unit: str
    source: str
    source_url: Optional[str]
    confidence: ConfidenceLevel
    notes: str = ""
    range_low: Optional[float] = None
    range_high: Optional[float] = None


@dataclass
class CalculationMethod:
    """Documents a calculation methodology."""
    name: str
    formula: str
    description: str
    inputs: List[str]
    assumptions: List[Assumption]
    confidence: ConfidenceLevel
    limitations: List[str]
    validation_status: str = "Not validated"


# =============================================================================
# DOCUMENTED ASSUMPTIONS
# =============================================================================

ASSUMPTIONS = {
    # --- HIGH CONFIDENCE (Official Sources) ---
    "working_hours_france": Assumption(
        name="Annual Working Hours (France)",
        value=1607,
        unit="hours/year",
        source="French Labor Code (Code du Travail)",
        source_url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033020517",
        confidence=ConfidenceLevel.HIGH,
        notes="Legal standard for 35-hour workweek"
    ),
    
    "electricity_price_france": Assumption(
        name="Electricity Price (France, Enterprise)",
        value=0.22,
        unit="€/kWh",
        source="Eurostat - Electricity prices for non-household consumers",
        source_url="https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Electricity_price_statistics",
        confidence=ConfidenceLevel.HIGH,
        range_low=0.18,
        range_high=0.28,
        notes="Enterprise rate, may vary by contract"
    ),
    
    "grid_carbon_france": Assumption(
        name="Grid Carbon Factor (France)",
        value=0.052,
        unit="kg CO₂/kWh",
        source="European Environment Agency 2023",
        source_url="https://www.eea.europa.eu/",
        confidence=ConfidenceLevel.HIGH,
        range_low=0.035,
        range_high=0.085,
        notes="France has low-carbon grid due to nuclear. Varies seasonally."
    ),
    
    # --- MEDIUM CONFIDENCE (Industry Benchmarks) ---
    "depreciation_rate": Assumption(
        name="IT Asset Depreciation Rate",
        value=0.30,
        unit="per year",
        source="Gartner IT Asset Valuation Guidelines 2023",
        source_url=None,
        confidence=ConfidenceLevel.MEDIUM,
        range_low=0.25,
        range_high=0.40,
        notes="30% annual depreciation is industry standard, but resale values vary widely"
    ),
    
    "refurb_co2_savings": Assumption(
        name="Refurbished CO₂ Savings Rate",
        value=0.80,
        unit="fraction",
        source="Dell Circular Economy Report 2023",
        source_url="https://www.dell.com/en-us/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm",
        confidence=ConfidenceLevel.MEDIUM,
        range_low=0.70,
        range_high=0.91,
        notes="Dell claims 'up to 80%'. Back Market claims up to 91%. Apple claims 85%."
    ),
    
    "refurb_price_ratio": Assumption(
        name="Refurbished Price Ratio",
        value=0.59,
        unit="fraction of new price",
        source="Back Market France 2024 - Dell Latitude pricing",
        source_url="https://www.backmarket.fr/",
        confidence=ConfidenceLevel.MEDIUM,
        range_low=0.45,
        range_high=0.70,
        notes="Varies by model, condition, and availability"
    ),
    
    # --- LOW CONFIDENCE (Estimates) ---
    "productivity_loss_rate": Assumption(
        name="Productivity Loss per Year (aging device)",
        value=0.03,
        unit="fraction per year beyond optimal",
        source="Gartner Digital Workplace Study 2023",
        source_url=None,
        confidence=ConfidenceLevel.LOW,
        range_low=0.01,
        range_high=0.06,
        notes="CAUTION: Productivity loss is very difficult to measure. "
              "Gartner reports 3-6% range. We use conservative 3%."
    ),
    
    "lag_sensitivity": Assumption(
        name="Persona Lag Sensitivity Multiplier",
        value="varies by role",
        unit="multiplier",
        source="Internal estimate based on role analysis",
        source_url=None,
        confidence=ConfidenceLevel.LOW,
        notes="Theoretical construct. A developer (2.5x) loses more productivity "
              "from lag than a vendor (0.2x). NOT empirically validated."
    ),
    
    # --- THEORETICAL (Model-based) ---
    "stranded_value": Assumption(
        name="Stranded Value Calculation",
        value="fleet × price × depreciation",
        unit="EUR",
        source="Élysia methodology",
        source_url=None,
        confidence=ConfidenceLevel.THEORETICAL,
        notes="IMPORTANT: Assumes devices could be resold at depreciated value. "
              "In practice, many enterprises don't resell (data security) and "
              "bulk resale prices are much lower than calculated."
    ),
}


# =============================================================================
# DOCUMENTED CALCULATION METHODS
# =============================================================================

CALCULATION_METHODS = {
    "tco_keep": CalculationMethod(
        name="TCO - Keep Current Device",
        formula="TCO_keep = Energy_cost + Productivity_loss + Residual_loss",
        description="Total cost of ownership for keeping an existing device for one more year",
        inputs=["device_model", "device_age", "persona", "country"],
        assumptions=[
            ASSUMPTIONS["electricity_price_france"],
            ASSUMPTIONS["productivity_loss_rate"],
            ASSUMPTIONS["depreciation_rate"],
        ],
        confidence=ConfidenceLevel.MEDIUM,
        limitations=[
            "Productivity loss is theoretical and not empirically validated",
            "Does not account for maintenance/repair costs",
            "Assumes linear productivity degradation (reality is often non-linear)",
        ],
        validation_status="Partially validated against Dell TCO models"
    ),
    
    "tco_new": CalculationMethod(
        name="TCO - Buy New Device",
        formula="TCO_new = (Purchase_price / Lifespan) + Energy_cost + Disposal_cost - Residual_benefit",
        description="Annualized total cost of ownership for purchasing a new device",
        inputs=["device_model", "persona", "country"],
        assumptions=[
            ASSUMPTIONS["electricity_price_france"],
            ASSUMPTIONS["depreciation_rate"],
        ],
        confidence=ConfidenceLevel.HIGH,
        limitations=[
            "Assumes device lasts full expected lifespan",
            "Does not account for financing costs or opportunity cost of capital",
        ],
        validation_status="Validated against industry TCO calculators"
    ),
    
    "tco_refurb": CalculationMethod(
        name="TCO - Buy Refurbished Device",
        formula="TCO_refurb = (Refurb_price / Warranty_years) + Energy_cost×1.1 + Disposal_cost - Residual_benefit",
        description="Annualized total cost for refurbished device",
        inputs=["device_model", "persona", "country"],
        assumptions=[
            ASSUMPTIONS["refurb_price_ratio"],
            ASSUMPTIONS["electricity_price_france"],
        ],
        confidence=ConfidenceLevel.MEDIUM,
        limitations=[
            "Assumes 10% energy penalty for older hardware (may be higher or lower)",
            "Shorter warranty period (2-3 years vs 3-4 for new)",
            "Availability varies significantly by model and region",
        ],
        validation_status="Based on Back Market data, not validated at scale"
    ),
    
    "co2_manufacturing": CalculationMethod(
        name="CO₂ - Manufacturing Emissions",
        formula="CO2_mfg = Device_manufacturing_kg / Lifespan_years",
        description="Annualized manufacturing carbon footprint",
        inputs=["device_model"],
        assumptions=[],
        confidence=ConfidenceLevel.HIGH,
        limitations=[
            "Uses manufacturer-reported data (Apple, Dell environmental reports)",
            "Does not include supply chain transport beyond what manufacturers report",
        ],
        validation_status="Uses official manufacturer environmental reports"
    ),
    
    "co2_usage": CalculationMethod(
        name="CO₂ - Usage Emissions",
        formula="CO2_usage = Power_kW × Annual_hours × Grid_factor",
        description="Annual carbon emissions from device usage",
        inputs=["device_model", "persona", "country"],
        assumptions=[
            ASSUMPTIONS["grid_carbon_france"],
            ASSUMPTIONS["working_hours_france"],
        ],
        confidence=ConfidenceLevel.HIGH,
        limitations=[
            "Uses average grid factor (real-time varies by hour)",
            "Assumes device is on during all working hours (may overestimate)",
        ],
        validation_status="Formula is industry standard (GHG Protocol)"
    ),
    
    "stranded_value": CalculationMethod(
        name="Stranded Value Calculation",
        formula="Stranded_value = Fleet_size × Avg_device_price × (0.70)^Avg_age",
        description="Theoretical residual value locked in fleet",
        inputs=["fleet_size", "avg_age"],
        assumptions=[
            ASSUMPTIONS["depreciation_rate"],
            ASSUMPTIONS["stranded_value"],
        ],
        confidence=ConfidenceLevel.LOW,
        limitations=[
            "⚠️ SIGNIFICANT LIMITATION: Assumes devices can be resold at calculated value",
            "Many enterprises don't resell (data security, logistics)",
            "Bulk resale prices are typically 30-50% lower than individual resale",
            "Some devices have zero market value",
            "Use this metric directionally, not as precise financial projection",
        ],
        validation_status="NOT VALIDATED - Use as directional indicator only"
    ),
    
    "productivity_loss": CalculationMethod(
        name="Productivity Loss Calculation",
        formula="Loss = Salary × (Age - Optimal_years) × 0.03 × Lag_sensitivity",
        description="Estimated annual cost of productivity loss from aging device",
        inputs=["device_model", "device_age", "persona"],
        assumptions=[
            ASSUMPTIONS["productivity_loss_rate"],
            ASSUMPTIONS["lag_sensitivity"],
        ],
        confidence=ConfidenceLevel.THEORETICAL,
        limitations=[
            "⚠️ HIGHLY THEORETICAL: Productivity loss is very difficult to measure",
            "Based on Gartner survey data, not direct measurement",
            "Lag sensitivity multipliers are internal estimates, not validated",
            "Actual productivity impact depends on specific work tasks",
            "Consider this metric as illustrative, not precise",
        ],
        validation_status="NOT VALIDATED - Theoretical model only"
    ),
}


# =============================================================================
# RANGE CALCULATIONS
# =============================================================================

def calculate_with_range(base_value: float, assumption_key: str) -> Dict:
    """
    Calculate a value with low/mid/high range based on assumption uncertainty.
    
    Returns:
        {
            "value": float,        # Best estimate
            "low": float,          # Conservative estimate
            "high": float,         # Optimistic estimate
            "confidence": str,     # Confidence level
            "note": str            # Explanation
        }
    """
    assumption = ASSUMPTIONS.get(assumption_key)
    if not assumption:
        return {"value": base_value, "low": base_value, "high": base_value, 
                "confidence": "UNKNOWN", "note": "No assumption data available"}
    
    # Calculate range based on confidence level
    if assumption.confidence == ConfidenceLevel.HIGH:
        variance = 0.10  # ±10%
    elif assumption.confidence == ConfidenceLevel.MEDIUM:
        variance = 0.25  # ±25%
    elif assumption.confidence == ConfidenceLevel.LOW:
        variance = 0.50  # ±50%
    else:  # THEORETICAL
        variance = 0.75  # ±75%
    
    # Use explicit ranges if provided
    if assumption.range_low and assumption.range_high:
        ratio_low = assumption.range_low / assumption.value if assumption.value else 1
        ratio_high = assumption.range_high / assumption.value if assumption.value else 1
        low = base_value * ratio_low
        high = base_value * ratio_high
    else:
        low = base_value * (1 - variance)
        high = base_value * (1 + variance)
    
    return {
        "value": base_value,
        "low": round(low, 2),
        "high": round(high, 2),
        "confidence": assumption.confidence.value,
        "note": assumption.notes
    }


def get_stranded_value_range(fleet_size: int, avg_age: float, 
                              avg_price: float = 1150) -> Dict:
    """
    Calculate stranded value with realistic range.
    
    The "stranded value" metric has significant uncertainty because:
    1. Many companies don't resell devices
    2. Bulk resale prices are lower than individual
    3. Some devices have zero market value
    """
    # Base calculation (optimistic)
    depreciation = 0.70 ** avg_age
    base_value = fleet_size * avg_price * depreciation
    
    # Realistic adjustments
    # - Only ~60% of devices typically get resold
    # - Bulk prices are ~50-70% of individual resale
    resale_participation_low = 0.30   # Conservative: 30% get resold
    resale_participation_mid = 0.50   # Realistic: 50% get resold  
    resale_participation_high = 0.70  # Optimistic: 70% get resold
    
    bulk_discount_low = 0.40   # Conservative: 40% of calculated value
    bulk_discount_mid = 0.60   # Realistic: 60% of calculated value
    bulk_discount_high = 0.80  # Optimistic: 80% of calculated value
    
    return {
        "theoretical_value": round(base_value, 0),
        "realistic_low": round(base_value * resale_participation_low * bulk_discount_low, 0),
        "realistic_mid": round(base_value * resale_participation_mid * bulk_discount_mid, 0),
        "realistic_high": round(base_value * resale_participation_high * bulk_discount_high, 0),
        "confidence": "LOW",
        "note": "Stranded value assumes devices can be resold. In practice, "
                "actual recoverable value is typically 15-35% of theoretical value.",
        "display_range": f"€{base_value * 0.15:,.0f} - €{base_value * 0.35:,.0f}",
    }


def get_co2_savings_range(fleet_size: int, refresh_cycle: int,
                          refurb_rate: float = 0.40) -> Dict:
    """
    Calculate avoidable CO₂ with range based on refurb savings uncertainty.
    """
    annual_replacements = fleet_size / refresh_cycle
    avg_co2_per_device = 365  # kg, Dell Latitude average
    
    # Savings rates from different sources
    savings_conservative = 0.70  # Conservative estimate
    savings_mid = 0.80           # Dell claims
    savings_optimistic = 0.91   # Back Market claims
    
    base_calc = annual_replacements * refurb_rate * avg_co2_per_device
    
    return {
        "low_tonnes": round(base_calc * savings_conservative / 1000, 1),
        "mid_tonnes": round(base_calc * savings_mid / 1000, 1),
        "high_tonnes": round(base_calc * savings_optimistic / 1000, 1),
        "confidence": "MEDIUM",
        "note": "CO₂ savings range reflects different industry claims: "
                "Dell (80%), Apple (85%), Back Market (91%).",
        "source": "Dell Circular Economy Report 2023, Apple Environmental Report 2023",
    }


# =============================================================================
# DISCLAIMER TEXTS
# =============================================================================

DISCLAIMERS = {
    "general": """
**Disclaimer**: Élysia provides estimates based on industry benchmarks and 
publicly available data. Actual results may vary significantly based on your 
specific circumstances, market conditions, and implementation approach. 
These projections should be used for directional planning, not as precise 
financial forecasts.
""",
    
    "stranded_value": """
**About Stranded Value**: This metric represents the theoretical residual 
value of devices based on standard depreciation curves. In practice, 
recoverable value depends on your resale strategy, data security requirements, 
and market conditions. Many enterprises choose not to resell for security 
reasons, making actual recoverable value €0.
""",
    
    "productivity": """
**About Productivity Estimates**: Productivity loss calculations are based on 
industry research (Gartner Digital Workplace Study 2023) but are inherently 
difficult to measure precisely. The actual impact depends on specific work 
tasks, user behavior, and IT support quality. Consider these figures as 
illustrative rather than precise.
""",
    
    "co2": """
**About CO₂ Calculations**: Carbon footprint data comes from manufacturer 
environmental reports (Apple, Dell) and follows GHG Protocol standards. 
Grid carbon factors use annual averages; real-time emissions vary by hour 
and season. For Scope 3 reporting, verify alignment with your company's 
methodology.
""",
    
    "refurbished": """
**About Refurbished Devices**: Availability, pricing, and quality of 
refurbished devices varies significantly by model, region, and supplier. 
The 80% CO₂ savings figure is a conservative estimate based on Dell's 
Circular Economy Report. Enterprise-grade refurbished supply may be 
limited for specific models.
""",
}


# =============================================================================
# METHODOLOGY REPORT GENERATOR
# =============================================================================

def generate_methodology_markdown() -> str:
    """Generate a full methodology document in Markdown format."""
    md = """# Élysia Methodology Documentation

## Overview

Élysia uses a combination of manufacturer data, industry benchmarks, and 
established calculation methods to estimate the environmental and financial 
impact of IT fleet decisions.

**Important**: All estimates include inherent uncertainty. This document 
provides full transparency into our assumptions, sources, and limitations.

---

## Confidence Levels

| Level | Description | Typical Variance |
|-------|-------------|------------------|
| **HIGH** | Official sources, measured data | ±10% |
| **MEDIUM** | Industry benchmarks, may vary | ±25% |
| **LOW** | Estimates, significant uncertainty | ±50% |
| **THEORETICAL** | Model-based, not validated | ±75% |

---

## Key Assumptions

"""
    
    for key, assumption in ASSUMPTIONS.items():
        md += f"""### {assumption.name}
- **Value**: {assumption.value} {assumption.unit}
- **Source**: {assumption.source}
- **Confidence**: {assumption.confidence.value}
"""
        if assumption.range_low and assumption.range_high:
            md += f"- **Range**: {assumption.range_low} - {assumption.range_high} {assumption.unit}\n"
        if assumption.notes:
            md += f"- **Notes**: {assumption.notes}\n"
        md += "\n"
    
    md += """---

## Calculation Methods

"""
    
    for key, method in CALCULATION_METHODS.items():
        md += f"""### {method.name}

**Formula**: `{method.formula}`

{method.description}

**Confidence**: {method.confidence.value}

**Limitations**:
"""
        for limitation in method.limitations:
            md += f"- {limitation}\n"
        
        md += f"\n**Validation Status**: {method.validation_status}\n\n"
    
    md += """---

## Data Sources

| Data Type | Source | URL |
|-----------|--------|-----|
| Device CO₂ | Apple Environmental Reports | apple.com/environment |
| Device CO₂ | Dell Product Carbon Footprints | dell.com/environment |
| Grid Factors | European Environment Agency | eea.europa.eu |
| Electricity Prices | Eurostat | ec.europa.eu/eurostat |
| Depreciation | Gartner IT Asset Valuation | gartner.com |
| Refurb Pricing | Back Market France | backmarket.fr |

---

## Recommendations for Use

1. **Use ranges, not point estimates** - Always consider the low/mid/high range
2. **Validate with pilots** - Test assumptions with a small fleet before scaling
3. **Update assumptions** - Market prices and grid factors change over time
4. **Consult experts** - For financial decisions, involve finance and procurement

---

*Generated by Élysia Methodology Module*
"""
    
    return md


# =============================================================================
# HELPER FUNCTIONS FOR UI
# =============================================================================

def get_confidence_badge(confidence: ConfidenceLevel) -> str:
    """Return HTML badge for confidence level."""
    colors = {
        ConfidenceLevel.HIGH: "#4A7C59",
        ConfidenceLevel.MEDIUM: "#C4943A", 
        ConfidenceLevel.LOW: "#9E4A4A",
        ConfidenceLevel.THEORETICAL: "#6B6560",
    }
    color = colors.get(confidence, "#6B6560")
    return f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:0.7rem;">{confidence.value}</span>'


def get_assumption_tooltip(key: str) -> str:
    """Get tooltip text for an assumption."""
    assumption = ASSUMPTIONS.get(key)
    if not assumption:
        return ""
    
    tooltip = f"{assumption.name}: {assumption.value} {assumption.unit}"
    if assumption.range_low and assumption.range_high:
        tooltip += f" (range: {assumption.range_low}-{assumption.range_high})"
    tooltip += f" | Source: {assumption.source}"
    if assumption.notes:
        tooltip += f" | Note: {assumption.notes}"
    
    return tooltip