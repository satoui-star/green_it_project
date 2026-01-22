"""
Élysia - Reference Data Module (Enhanced)
==========================================
LVMH · Sustainable IT Intelligence

All reference data with documented sources AND confidence levels.
IMPORTANT: Personas and Devices are from LVMH-provided data - DO NOT MODIFY.

ENHANCEMENT: Added confidence levels, ranges, and validation status.
"""

from enum import Enum
from typing import Dict, Optional

# =============================================================================
# CONFIDENCE FRAMEWORK
# =============================================================================

class Confidence(Enum):
    """Data confidence levels."""
    HIGH = "HIGH"           # Official source, measured data
    MEDIUM = "MEDIUM"       # Industry benchmark, ±25% variance
    LOW = "LOW"             # Estimate, ±50% variance
    THEORETICAL = "THEORETICAL"  # Model-based, not validated


# =============================================================================
# 1. WORKING HOURS & ELECTRICITY
# =============================================================================
# SOURCE: French Labor Code (Code du Travail)
# https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033020517
HOURS_ANNUAL = 1607  # Legal work year in France (35h × 45.9 weeks)
HOURS_SOURCE = "French Labor Code (Code du Travail)"
HOURS_CONFIDENCE = Confidence.HIGH

# SOURCE: Eurostat - Electricity prices for non-household consumers, France 2024
# https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Electricity_price_statistics
PRICE_KWH_EUR = 0.22  # €/kWh - Enterprise rate France 2024
PRICE_KWH_RANGE = {"low": 0.18, "mid": 0.22, "high": 0.28}  # Range by contract
PRICE_SOURCE = "Eurostat 2024"
PRICE_CONFIDENCE = Confidence.HIGH

DEFAULT_REFRESH_YEARS = 4
DEFAULT_TARGET_REDUCTION = 0.20


# =============================================================================
# 2. PERSONAS (LVMH PROVIDED - DO NOT MODIFY)
# =============================================================================
PERSONAS = {
    "Vendor (Phone/Tablet)": {
        "description": "Sales floor staff, retail associates. Device used for POS, inventory lookup.",
        "salary_eur": 35000,
        "daily_hours": 8,
        "lag_sensitivity": 0.2,
        "typical_device": "Smartphone (Generic)",
        "_confidence_note": "Lag sensitivity is THEORETICAL - not empirically validated",
    },
    "Admin Normal (HR/Finance)": {
        "description": "Back-office staff. Email, spreadsheets, ERP systems.",
        "salary_eur": 55000,
        "daily_hours": 8,
        "lag_sensitivity": 1.0,
        "typical_device": "Laptop (Standard)",
        "_confidence_note": "Lag sensitivity is THEORETICAL - not empirically validated",
    },
    "Admin High (Dev/Data)": {
        "description": "Developers, data scientists, IT. Heavy compute needs.",
        "salary_eur": 95000,
        "daily_hours": 9,
        "lag_sensitivity": 2.5,
        "typical_device": "Workstation",
        "_confidence_note": "Lag sensitivity is THEORETICAL - not empirically validated",
    },
    "Depot Worker (Logistics)": {
        "description": "Warehouse staff, logistics. Device critical for operations.",
        "salary_eur": 40000,
        "daily_hours": 16,
        "lag_sensitivity": 1.5,
        "typical_device": "Scanner (Logistics)",
        "_confidence_note": "Lag sensitivity is THEORETICAL - not empirically validated",
    },
}
PERSONAS_SOURCE = "LVMH Green IT Hackathon 2025 - Provided dataset"
PERSONAS_CONFIDENCE = {
    "salary_eur": Confidence.MEDIUM,  # Based on Eurostat averages
    "lag_sensitivity": Confidence.THEORETICAL,  # ⚠️ Not validated
}


# =============================================================================
# 3. DEVICES (LVMH PROVIDED - DO NOT MODIFY)
# =============================================================================
DEVICES = {
    "iPhone SE (Legacy)": {
        "price_new_eur": 529,
        "co2_manufacturing_kg": 73.0,
        "power_kw": 0.005,
        "lifespan_months": 48,
        "category": "Smartphone",
        "refurb_available": True,
        "has_data": True,
        "source": "Apple iPhone SE Environmental Report 2022",
        "_co2_confidence": Confidence.HIGH,  # Official Apple data
    },
    "iPhone 16e (New Target)": {
        "price_new_eur": 969,
        "co2_manufacturing_kg": 249.5,
        "power_kw": 0.005,
        "lifespan_months": 48,
        "category": "Smartphone",
        "refurb_available": False,
        "has_data": True,
        "source": "Apple iPhone 16 Environmental Report 2024 (estimated)",
        "_co2_confidence": Confidence.MEDIUM,  # Estimated from similar models
    },
    "iPhone 14 (Alternative)": {
        "price_new_eur": 749,
        "co2_manufacturing_kg": 226.5,
        "power_kw": 0.005,
        "lifespan_months": 48,
        "category": "Smartphone",
        "refurb_available": True,
        "has_data": True,
        "source": "Apple iPhone 14 Environmental Report 2022",
        "_co2_confidence": Confidence.HIGH,
    },
    "iPhone 13 (Refurbished)": {
        "price_new_eur": 450,
        "co2_manufacturing_kg": 79.0,
        "power_kw": 0.005,
        "lifespan_months": 24,
        "category": "Smartphone",
        "refurb_available": True,
        "is_refurbished": True,
        "has_data": True,
        "source": "Apple + Back Market refurb data",
        "_co2_confidence": Confidence.MEDIUM,
    },
    "iPhone 12 (Refurbished)": {
        "price_new_eur": 350,
        "co2_manufacturing_kg": 12.0,
        "power_kw": 0.005,
        "lifespan_months": 24,
        "category": "Smartphone",
        "refurb_available": True,
        "is_refurbished": True,
        "has_data": True,
        "source": "Apple + Back Market refurb data",
        "_co2_confidence": Confidence.MEDIUM,
    },
    "Laptop (Standard)": {
        "price_new_eur": 1000,
        "co2_manufacturing_kg": 250,
        "power_kw": 0.030,
        "lifespan_months": 48,
        "category": "Laptop",
        "refurb_available": True,
        "has_data": True,
        "source": "Dell Latitude 5420 Product Carbon Footprint Report",
        "_co2_confidence": Confidence.HIGH,
    },
    "Workstation": {
        "price_new_eur": 2200,
        "co2_manufacturing_kg": 450,
        "power_kw": 0.080,
        "lifespan_months": 60,
        "category": "Workstation",
        "refurb_available": True,
        "has_data": True,
        "source": "HP ZBook Fury Life Cycle Assessment",
        "_co2_confidence": Confidence.HIGH,
    },
    "Smartphone (Generic)": {
        "price_new_eur": 500,
        "co2_manufacturing_kg": 60,
        "power_kw": 0.005,
        "lifespan_months": 36,
        "category": "Smartphone",
        "refurb_available": True,
        "has_data": True,
        "source": "Boavizta API - Average smartphone",
        "_co2_confidence": Confidence.MEDIUM,
    },
    "Tablet": {
        "price_new_eur": 500,
        "co2_manufacturing_kg": 150,
        "power_kw": 0.010,
        "lifespan_months": 48,
        "category": "Tablet",
        "refurb_available": True,
        "has_data": True,
        "source": "Apple iPad Air Environmental Report",
        "_co2_confidence": Confidence.HIGH,
    },
    "Scanner (Logistics)": {
        "price_new_eur": 1200,
        "co2_manufacturing_kg": 180,
        "power_kw": 0.015,
        "lifespan_months": 48,
        "category": "Scanner",
        "refurb_available": True,
        "has_data": True,
        "source": "Zebra TC52 Product Environmental Report",
        "_co2_confidence": Confidence.HIGH,
    },
    "Screen (Monitor)": {
        "price_new_eur": 300,
        "co2_manufacturing_kg": 350,
        "power_kw": 0.035,
        "lifespan_months": 72,
        "category": "Monitor",
        "refurb_available": True,
        "has_data": False,
        "source": "Dell 24 Monitor Life Cycle Assessment",
        "_co2_confidence": Confidence.HIGH,
    },
    "Meeting Room Screen": {
        "price_new_eur": 3000,
        "co2_manufacturing_kg": 800,
        "power_kw": 0.150,
        "lifespan_months": 84,
        "category": "Display",
        "refurb_available": False,
        "has_data": False,
        "source": "Samsung Large Format Display LCA",
        "_co2_confidence": Confidence.MEDIUM,
    },
    "Switch/Router": {
        "price_new_eur": 250,
        "co2_manufacturing_kg": 100,
        "power_kw": 0.050,
        "lifespan_months": 72,
        "category": "Network",
        "refurb_available": True,
        "has_data": False,
        "source": "Cisco Catalyst Product Carbon Footprint",
        "_co2_confidence": Confidence.HIGH,
    },
}
DEVICES_SOURCE = "Multiple sources - see individual device entries"


# =============================================================================
# 4. DELL-SPECIFIC DEVICE DATA (FOR LVMH CONTEXT)
# =============================================================================
# SOURCE: Dell Product Carbon Footprints
# https://www.dell.com/en-us/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm
DELL_DEVICES = {
    "Dell Latitude 5540": {
        "co2_manufacturing_kg": 341,
        "co2_use_phase_kg": 156,
        "co2_total_kg": 497,
        "price_new_eur": 1100,
        "price_refurb_eur": 650,
        "source": "Dell Product Carbon Footprint - Latitude 5540",
        "source_date": "2024-03",
        "_confidence": Confidence.HIGH,
    },
    "Dell Latitude 7440": {
        "co2_manufacturing_kg": 365,
        "co2_use_phase_kg": 148,
        "co2_total_kg": 513,
        "price_new_eur": 1450,
        "price_refurb_eur": 850,
        "source": "Dell Product Carbon Footprint - Latitude 7440",
        "source_date": "2024-03",
        "_confidence": Confidence.HIGH,
    },
    "Dell Latitude 9440": {
        "co2_manufacturing_kg": 389,
        "co2_use_phase_kg": 142,
        "co2_total_kg": 531,
        "price_new_eur": 1900,
        "price_refurb_eur": 1100,
        "source": "Dell Product Carbon Footprint - Latitude 9440",
        "source_date": "2024-03",
        "_confidence": Confidence.HIGH,
    },
    "Dell OptiPlex 7010": {
        "co2_manufacturing_kg": 436,
        "co2_use_phase_kg": 210,
        "co2_total_kg": 646,
        "price_new_eur": 900,
        "price_refurb_eur": 500,
        "source": "Dell Product Carbon Footprint - OptiPlex 7010",
        "source_date": "2024-03",
        "_confidence": Confidence.HIGH,
    },
    "Dell Precision 5680": {
        "co2_manufacturing_kg": 521,
        "co2_use_phase_kg": 178,
        "co2_total_kg": 699,
        "price_new_eur": 2800,
        "price_refurb_eur": 1600,
        "source": "Dell Product Carbon Footprint - Precision 5680",
        "source_date": "2024-03",
        "_confidence": Confidence.HIGH,
    },
}
DELL_AVERAGE_LAPTOP_CO2 = 365  # kg - Average of Latitude models
DELL_SOURCE = "Dell Product Carbon Footprints (dell.com/environment)"


# =============================================================================
# 5. DISPOSAL COSTS (LVMH PARTNER PRICING)
# =============================================================================
DISPOSAL_COST_NO_DATA = 8    # € - Devices without data (printer, screen, etc.)
DISPOSAL_COST_WITH_DATA = 14  # € - Devices with data (laptop, phone) - 1 pass wipe
DISPOSAL_SOURCE = "LVMH Refurb Partner - January 2025"
DISPOSAL_CONFIDENCE = Confidence.HIGH  # Actual partner pricing


# =============================================================================
# 6. DEPRECIATION MODEL
# =============================================================================
# SOURCE: Gartner IT Asset Valuation Guidelines 2023
# FORMULA: Remaining Value = 100% × (0.70)^age
# This means 30% depreciation per year
DEPRECIATION_RATE_PER_YEAR = 0.30
DEPRECIATION_BASE = 0.70  # 1 - 0.30

# ⚠️ IMPORTANT CAVEAT
DEPRECIATION_CAVEAT = """
This depreciation model assumes devices CAN be resold at the calculated value.
In practice:
- Many enterprises don't resell (data security, logistics complexity)
- Bulk resale prices are 30-50% lower than individual resale
- Some device categories have zero market demand
Use this for directional analysis, not precise financial planning.
"""

DEPRECIATION_CURVE = {
    0: 1.00,   # New
    1: 0.70,   # 1 year: 100% × 0.70^1
    2: 0.49,   # 2 years: 100% × 0.70^2
    3: 0.34,   # 3 years: 100% × 0.70^3
    4: 0.24,   # 4 years: 100% × 0.70^4
    5: 0.17,   # 5 years: 100% × 0.70^5
    6: 0.12,   # 6 years: 100% × 0.70^6
    7: 0.08,   # 7 years: 100% × 0.70^7
    8: 0.06,   # 8 years: 100% × 0.70^8
}
DEPRECIATION_SOURCE = "Gartner IT Asset Valuation Guidelines 2023"
DEPRECIATION_CONFIDENCE = Confidence.MEDIUM  # Industry benchmark, varies in practice

PREMIUM_KEYWORDS = ["iPhone", "MacBook", "iPad", "ThinkPad", "Surface", "Dell Latitude 9"]
PREMIUM_RETENTION_BONUS = 0.10  # Premium devices retain 10% more value


# =============================================================================
# 7. PRODUCTIVITY LOSS MODEL
# =============================================================================
# SOURCE: Gartner Digital Workplace Study 2023
# "Aging devices (4+ years) cause 3-6% productivity loss"

# ⚠️ IMPORTANT: This is the WEAKEST assumption in the model
PRODUCTIVITY_CAVEAT = """
⚠️ THEORETICAL MODEL - NOT EMPIRICALLY VALIDATED

Productivity loss from aging devices is very difficult to measure:
- Based on Gartner survey data (self-reported, not measured)
- Actual impact depends on specific work tasks
- "Lag sensitivity" multipliers are internal estimates
- Consider these figures as ILLUSTRATIVE, not precise

For financial decisions, we recommend discounting these figures by 50%
or treating them as qualitative indicators only.
"""

PRODUCTIVITY_CONFIG = {
    "optimal_years": 3,           # Devices under 3 years = no productivity loss
    "degradation_per_year": 0.03, # 3% loss per year beyond optimal
    "max_degradation": 0.15,      # Cap at 15% loss
    # RANGE for sensitivity analysis
    "_range_low": 0.01,           # Conservative: 1% per year
    "_range_high": 0.06,          # Aggressive: 6% per year (Gartner upper bound)
}
PRODUCTIVITY_SOURCE = "Gartner Digital Workplace Study 2023"
PRODUCTIVITY_CONFIDENCE = Confidence.LOW  # ⚠️ High uncertainty


# =============================================================================
# 8. REFURBISHED PARAMETERS
# =============================================================================
# SOURCE: Dell Circular Economy Report 2023, Apple Environmental Report 2023
REFURB_CONFIG = {
    "co2_savings_rate": 0.80,      # 80% CO2 savings (conservative - Dell claims "up to 80%")
    "price_ratio": 0.59,           # Refurb costs 59% of new (from Back Market data)
    "energy_penalty": 0.10,        # 10% more energy use (older tech)
    "warranty_years": 2,           # Standard refurb warranty
    "equivalent_age_years": 1.5,   # Refurb device equivalent to 1.5 year old
    # RANGES for sensitivity analysis
    "_co2_savings_range": {"low": 0.70, "mid": 0.80, "high": 0.91},
    "_price_ratio_range": {"low": 0.45, "mid": 0.59, "high": 0.70},
}

REFURB_AVAILABILITY_NOTE = """
⚠️ AVAILABILITY VARIES SIGNIFICANTLY
- Not all models available refurbished at enterprise scale
- Quality and warranty vary by supplier
- Lead times may be longer than new devices
Verify availability with suppliers before committing to refurb targets.
"""

REFURB_SOURCES = {
    "co2_savings": "Dell Circular Economy Report 2023 - 'Up to 80% reduction'",
    "price_ratio": "Back Market France 2024 - Average Dell Latitude pricing",
    "apple_claim": "Apple Environmental Report 2023 - '85% reduction'",
    "back_market_claim": "Back Market Impact Report 2023 - 'Up to 91% reduction'",
}
REFURB_CONFIDENCE = Confidence.MEDIUM


# =============================================================================
# 9. URGENCY FRAMEWORK
# =============================================================================
# SOURCE: ITIL v4 Framework - Incident Priority Matrix
URGENCY_CONFIG = {
    "age_critical_years": 5,      # Device is critical if >= 5 years old
    "age_high_years": 4,          # Device is high priority if >= 4 years old
    "performance_threshold": 0.70, # Performance below 70% = urgent
    "eol_threshold_months": 6,    # Within 6 months of EOL = urgent
}
URGENCY_THRESHOLDS = {
    "HIGH": 2.0,    # Score >= 2.0 = HIGH urgency
    "MEDIUM": 1.3,  # Score >= 1.3 = MEDIUM urgency
    "LOW": 0.0,     # Score < 1.3 = LOW urgency
}
URGENCY_SOURCE = "ITIL v4 Framework - Incident Priority Matrix"
URGENCY_CONFIDENCE = Confidence.MEDIUM


# =============================================================================
# 10. CARBON GRID FACTORS
# =============================================================================
# SOURCE: European Environment Agency 2023 + ElectricityMaps API
# Unit: kg CO2 per kWh
GRID_CARBON_FACTORS = {
    "FR": {"factor": 0.052, "name": "France", "note": "High nuclear, very low carbon",
           "_range": {"low": 0.035, "high": 0.085}},
    "DE": {"factor": 0.385, "name": "Germany", "note": "Still significant coal",
           "_range": {"low": 0.300, "high": 0.450}},
    "UK": {"factor": 0.268, "name": "United Kingdom", "note": "Gas + renewables mix"},
    "US": {"factor": 0.410, "name": "United States", "note": "Varies by state"},
    "CN": {"factor": 0.550, "name": "China", "note": "Coal-heavy"},
    "JP": {"factor": 0.450, "name": "Japan", "note": "Post-Fukushima mix"},
    "IT": {"factor": 0.371, "name": "Italy", "note": "Gas-dominated"},
    "ES": {"factor": 0.185, "name": "Spain", "note": "Growing renewables"},
    "CH": {"factor": 0.035, "name": "Switzerland", "note": "Hydro-dominated"},
    "SE": {"factor": 0.020, "name": "Sweden", "note": "Hydro + nuclear"},
    "NO": {"factor": 0.010, "name": "Norway", "note": "Almost 100% hydro"},
    "HK": {"factor": 0.510, "name": "Hong Kong"},
    "SG": {"factor": 0.408, "name": "Singapore"},
    "KR": {"factor": 0.460, "name": "South Korea"},
    "AU": {"factor": 0.510, "name": "Australia"},
    "BR": {"factor": 0.070, "name": "Brazil", "note": "High hydro"},
}
DEFAULT_GRID_FACTOR = 0.270  # EU average
GRID_SOURCE = "European Environment Agency 2023 + ElectricityMaps API"
GRID_CONFIDENCE = Confidence.HIGH
GRID_NOTE = "Annual averages. Real-time emissions vary by hour and season."


# =============================================================================
# 11. FLEET SIZE MAPPING (For Quick Start)
# =============================================================================
FLEET_SIZE_OPTIONS = {
    "small": {
        "label": "Small (< 5,000 devices)",
        "estimate": 3000,
        "description": "Single Maison or department"
    },
    "medium": {
        "label": "Medium (5,000 - 20,000)",
        "estimate": 12500,
        "description": "Multiple Maisons or large division"
    },
    "large": {
        "label": "Large (20,000 - 50,000)",
        "estimate": 35000,
        "description": "Major business unit"
    },
    "enterprise": {
        "label": "Enterprise (50,000+)",
        "estimate": 75000,
        "description": "Group-wide scope"
    },
}


# =============================================================================
# 12. FLEET AGE MAPPING (For Quick Start)
# =============================================================================
FLEET_AGE_OPTIONS = {
    "young": {
        "label": "Young (< 2 years)",
        "estimate": 1.5,
        "description": "Recently refreshed",
        "backlog_pct": 0.05
    },
    "mature": {
        "label": "Mature (2-4 years)",
        "estimate": 3.0,
        "description": "Standard lifecycle",
        "backlog_pct": 0.15
    },
    "aging": {
        "label": "Aging (4-5 years)",
        "estimate": 4.5,
        "description": "Due for attention",
        "backlog_pct": 0.30
    },
    "legacy": {
        "label": "Legacy (5+ years)",
        "estimate": 6.0,
        "description": "Urgent action needed",
        "backlog_pct": 0.50
    },
}


# =============================================================================
# 13. STRATEGIES
# =============================================================================
STRATEGIES = {
    "do_nothing": {
        "name": "Do Nothing",
        "description": "Continue current approach - 100% new devices, standard lifecycle",
        "refurb_rate": 0.0,
        "lifecycle_years": 4,
        "recovery_rate": 0.0,
        "implementation_months": 0,
    },
    "refurb_20": {
        "name": "20% Refurbished",
        "description": "Conservative adoption - replace 20% of new purchases with refurbished",
        "refurb_rate": 0.20,
        "lifecycle_years": 4,
        "recovery_rate": 0.50,
        "implementation_months": 6,
    },
    "refurb_40": {
        "name": "40% Refurbished",
        "description": "Balanced approach - 40% refurbished, standard lifecycle",
        "refurb_rate": 0.40,
        "lifecycle_years": 4,
        "recovery_rate": 0.70,
        "implementation_months": 9,
    },
    "refurb_60": {
        "name": "60% Refurbished",
        "description": "Aggressive adoption - 60% refurbished for maximum CO2 impact",
        "refurb_rate": 0.60,
        "lifecycle_years": 4,
        "recovery_rate": 0.80,
        "implementation_months": 12,
    },
    "lifecycle_extension": {
        "name": "Lifecycle Extension",
        "description": "Extend device lifecycle from 4 to 5 years",
        "refurb_rate": 0.0,
        "lifecycle_years": 5,
        "recovery_rate": 0.50,
        "implementation_months": 6,
    },
    "combined_40_5yr": {
        "name": "Combined Strategy",
        "description": "Best of both: 40% refurbished + 5-year lifecycle",
        "refurb_rate": 0.40,
        "lifecycle_years": 5,
        "recovery_rate": 0.80,
        "implementation_months": 12,
    },
}
STRATEGIES_SOURCE = "Élysia methodology based on Gartner and Dell best practices"


# =============================================================================
# 14. LIFE 360 TARGETS
# =============================================================================
LIFE_360 = {
    "target_2026": -0.20,  # -20% CO2 by 2026
    "target_2030": -0.50,  # -50% CO2 by 2030
    "target_2050": -1.00,  # Net Zero by 2050
    "scope": "Scope 1 & 2 emissions",
    "source": "LVMH LIFE 360 Program",
}


# =============================================================================
# 15. AVERAGE VALUES FOR CALCULATIONS
# =============================================================================
AVERAGES = {
    "device_price_eur": 1150,          # Average Dell Latitude
    "device_co2_manufacturing_kg": 365, # Average Dell Latitude manufacturing
    "device_co2_annual_kg": 50,         # Annual usage CO2 (France grid)
    "salary_eur": 65000,                # Average salary (Eurostat France)
    "working_days_per_year": 220,
    "hours_per_day": 8,
}
AVERAGES_SOURCES = {
    "device_price": "Dell France Price List 2024",
    "device_co2": "Dell Product Carbon Footprints - Latitude average",
    "salary": "Eurostat Labour Cost Survey 2023",
}
AVERAGES_CONFIDENCE = Confidence.MEDIUM


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_device_names():
    """Return list of all device names."""
    return list(DEVICES.keys())


def get_persona_names():
    """Return list of all persona names."""
    return list(PERSONAS.keys())


def get_country_codes():
    """Return dict of country codes to names."""
    return {code: data["name"] for code, data in GRID_CARBON_FACTORS.items()}


# ---------------------------------------------------------------------------
# Convenience helpers used by the Streamlit UI
# ---------------------------------------------------------------------------

def get_country_name(country_code: str) -> str:
    """Return the display name for a country code (e.g., 'FR' -> 'France')."""
    mapping = get_country_codes()
    return mapping.get(country_code, country_code)


def get_country_code(country_code: str) -> str:
    """Backwards-compatible alias used by older UI code.

    Some UI versions used `get_country_code('FR')` to display 'France'.
    To avoid runtime NameError, this function simply delegates to
    `get_country_name`.
    """
    return get_country_name(country_code)


def get_grid_factor(country_code: str) -> float:
    """Get grid carbon factor for a country."""
    return GRID_CARBON_FACTORS.get(country_code, {}).get("factor", DEFAULT_GRID_FACTOR)


def get_grid_factor_with_range(country_code: str) -> Dict:
    """Get grid carbon factor with uncertainty range."""
    data = GRID_CARBON_FACTORS.get(country_code, {})
    factor = data.get("factor", DEFAULT_GRID_FACTOR)
    range_data = data.get("_range", {"low": factor * 0.8, "high": factor * 1.2})
    return {
        "value": factor,
        "low": range_data.get("low", factor * 0.8),
        "high": range_data.get("high", factor * 1.2),
        "confidence": GRID_CONFIDENCE.value,
    }


def get_depreciation_rate(age_years: float) -> float:
    """
    Calculate remaining value percentage based on age.
    Formula: Remaining Value = (0.70)^age
    """
    return DEPRECIATION_BASE ** age_years


def get_depreciation_rate_lookup(age_years: int) -> float:
    """Get depreciation rate from lookup table (for integer ages)."""
    return DEPRECIATION_CURVE.get(int(min(age_years, 8)), 0.06)


def is_premium_device(device_name: str) -> bool:
    """Check if device is a premium model (retains more value)."""
    return any(kw.lower() in device_name.lower() for kw in PREMIUM_KEYWORDS)


def get_disposal_cost(device_name: str) -> float:
    """Get disposal cost based on whether device has data."""
    device = DEVICES.get(device_name, {})
    return DISPOSAL_COST_WITH_DATA if device.get("has_data", True) else DISPOSAL_COST_NO_DATA


def get_fleet_estimate(selection: str) -> int:
    """Get estimated fleet size from selection."""
    return FLEET_SIZE_OPTIONS.get(selection, {}).get("estimate", 12500)


def get_age_estimate(selection: str) -> float:
    """Get estimated average age from selection."""
    return FLEET_AGE_OPTIONS.get(selection, {}).get("estimate", 3.5)


def calculate_stranded_value(fleet_size: int, avg_age: float, avg_price: float = None) -> dict:
    """
    Calculate stranded value in fleet WITH RANGE.
    
    Formula: Stranded Value = Fleet × Avg Price × Remaining Value %
    
    ⚠️ IMPORTANT: Returns theoretical value AND realistic range.
    """
    if avg_price is None:
        avg_price = AVERAGES["device_price_eur"]
    
    remaining_value_pct = get_depreciation_rate(avg_age)
    theoretical_value = fleet_size * avg_price * remaining_value_pct
    
    # Realistic range (see DEPRECIATION_CAVEAT)
    # Only 30-70% of devices typically get resold
    # Bulk prices are 40-80% of calculated value
    realistic_low = theoretical_value * 0.30 * 0.40  # 12% of theoretical
    realistic_mid = theoretical_value * 0.50 * 0.60  # 30% of theoretical
    realistic_high = theoretical_value * 0.70 * 0.80  # 56% of theoretical
    
    return {
        "value": round(theoretical_value, 2),
        "realistic_range": {
            "low": round(realistic_low, 2),
            "mid": round(realistic_mid, 2),
            "high": round(realistic_high, 2),
        },
        "calculation": {
            "fleet_size": fleet_size,
            "avg_price": avg_price,
            "avg_age": avg_age,
            "remaining_value_pct": round(remaining_value_pct, 4),
            "formula": "Fleet × Avg Price × Remaining Value %",
        },
        "source": DEPRECIATION_SOURCE,
        "confidence": DEPRECIATION_CONFIDENCE.value,
        "caveat": DEPRECIATION_CAVEAT,
    }


def calculate_avoidable_co2(fleet_size: int, refresh_cycle: int, refurb_rate: float = 0.40) -> dict:
    """
    Calculate avoidable CO2 if refurbished strategy is adopted.
    
    Formula: Avoidable CO2 = Annual Replacements × Refurb Rate × CO2/device × Savings Rate
    
    Returns dict with value and calculation breakdown.
    """
    annual_replacements = fleet_size / refresh_cycle
    co2_per_device = AVERAGES["device_co2_manufacturing_kg"]
    savings_rate = REFURB_CONFIG["co2_savings_rate"]
    
    avoidable_co2 = annual_replacements * refurb_rate * co2_per_device * savings_rate
    avoidable_co2_tonnes = avoidable_co2 / 1000
    
    return {
        "value_kg": round(avoidable_co2, 2),
        "value_tonnes": round(avoidable_co2_tonnes, 2),
        "calculation": {
            "fleet_size": fleet_size,
            "refresh_cycle": refresh_cycle,
            "annual_replacements": round(annual_replacements, 0),
            "refurb_rate": refurb_rate,
            "co2_per_device_kg": co2_per_device,
            "savings_rate": savings_rate,  # <-- This is the key that was missing!
            "formula": "Annual Replacements × Refurb Rate × CO2/device × 80%",
        },
        "source": REFURB_SOURCES["co2_savings"],
    }


def get_all_sources() -> dict:
    """Return all data sources for transparency."""
    return {
        "Working Hours": {"source": HOURS_SOURCE, "confidence": HOURS_CONFIDENCE.value},
        "Electricity Price": {"source": PRICE_SOURCE, "confidence": PRICE_CONFIDENCE.value},
        "Personas": {"source": PERSONAS_SOURCE, "confidence": "MIXED - see details"},
        "Devices": {"source": DEVICES_SOURCE, "confidence": "HIGH for CO2, varies for pricing"},
        "Dell Data": {"source": DELL_SOURCE, "confidence": Confidence.HIGH.value},
        "Disposal Costs": {"source": DISPOSAL_SOURCE, "confidence": DISPOSAL_CONFIDENCE.value},
        "Depreciation": {"source": DEPRECIATION_SOURCE, "confidence": DEPRECIATION_CONFIDENCE.value},
        "Productivity": {"source": PRODUCTIVITY_SOURCE, "confidence": PRODUCTIVITY_CONFIDENCE.value},
        "Refurbished CO2": {"source": REFURB_SOURCES["co2_savings"], "confidence": REFURB_CONFIDENCE.value},
        "Refurbished Pricing": {"source": REFURB_SOURCES["price_ratio"], "confidence": REFURB_CONFIDENCE.value},
        "Urgency Framework": {"source": URGENCY_SOURCE, "confidence": URGENCY_CONFIDENCE.value},
        "Grid Factors": {"source": GRID_SOURCE, "confidence": GRID_CONFIDENCE.value},
        "Strategies": {"source": STRATEGIES_SOURCE, "confidence": Confidence.MEDIUM.value},
        "LIFE 360": {"source": LIFE_360["source"], "confidence": Confidence.HIGH.value},
        "Average Prices": {"source": AVERAGES_SOURCES["device_price"], "confidence": AVERAGES_CONFIDENCE.value},
        "Average CO2": {"source": AVERAGES_SOURCES["device_co2"], "confidence": AVERAGES_CONFIDENCE.value},
        "Average Salary": {"source": AVERAGES_SOURCES["salary"], "confidence": AVERAGES_CONFIDENCE.value},
    }


def get_confidence_summary() -> dict:
    """Return summary of confidence levels across all data."""
    return {
        "high_confidence": [
            "Device CO2 (manufacturer reports)",
            "Grid carbon factors (EEA)",
            "Electricity prices (Eurostat)",
            "Working hours (French law)",
        ],
        "medium_confidence": [
            "Depreciation rates (Gartner benchmarks)",
            "Refurbished CO2 savings (Dell/Apple claims)",
            "Refurbished pricing (Back Market data)",
            "Average salaries (Eurostat)",
        ],
        "low_confidence": [
            "⚠️ Productivity loss rates (survey data, not measured)",
            "⚠️ Stranded value (assumes resale possible)",
        ],
        "theoretical": [
            "⚠️ Lag sensitivity multipliers (internal estimates)",
            "⚠️ Productivity cost calculations (model-based)",
        ],
    }