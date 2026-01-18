"""
EcoCycle Intelligence - Reference Data Module
==============================================
LVMH · Digital Sustainability Division

All reference data with documented sources.
IMPORTANT: Personas and Devices are from LVMH-provided data - DO NOT MODIFY.
"""

# =============================================================================
# 1. WORKING HOURS & ELECTRICITY
# =============================================================================
# SOURCE: French Labor Code (Code du Travail)
# https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033020517
HOURS_ANNUAL = 1607  # Legal work year in France (35h × 45.9 weeks)
HOURS_SOURCE = "French Labor Code (Code du Travail)"

# SOURCE: Eurostat - Electricity prices for non-household consumers, France 2024
# https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Electricity_price_statistics
PRICE_KWH_EUR = 0.22  # €/kWh - Enterprise rate France 2024
PRICE_SOURCE = "Eurostat 2024"

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
    },
    "Admin Normal (HR/Finance)": {
        "description": "Back-office staff. Email, spreadsheets, ERP systems.",
        "salary_eur": 55000,
        "daily_hours": 8,
        "lag_sensitivity": 1.0,
        "typical_device": "Laptop (Standard)",
    },
    "Admin High (Dev/Data)": {
        "description": "Developers, data scientists, IT. Heavy compute needs.",
        "salary_eur": 95000,
        "daily_hours": 9,
        "lag_sensitivity": 2.5,
        "typical_device": "Workstation",
    },
    "Depot Worker (Logistics)": {
        "description": "Warehouse staff, logistics. Device critical for operations.",
        "salary_eur": 40000,
        "daily_hours": 16,
        "lag_sensitivity": 1.5,
        "typical_device": "Scanner (Logistics)",
    },
}
PERSONAS_SOURCE = "LVMH Green IT Hackathon 2025 - Provided dataset"


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
    },
}
DEVICES_SOURCE = "Multiple sources - see individual device entries"


# =============================================================================
# 4. DISPOSAL COSTS (LVMH PARTNER PRICING)
# =============================================================================
DISPOSAL_COST_NO_DATA = 8    # € - Devices without data (printer, screen, etc.)
DISPOSAL_COST_WITH_DATA = 14  # € - Devices with data (laptop, phone) - 1 pass wipe
DISPOSAL_SOURCE = "LVMH Refurb Partner - January 2025"


# =============================================================================
# 5. DEPRECIATION CURVE
# =============================================================================
# SOURCE: Gartner IT Asset Valuation Guidelines 2023
# VALIDATED: Apple Trade-In Program, Back Market resale data
DEPRECIATION_CURVE = {
    0: 1.00,
    1: 0.70,
    2: 0.50,
    3: 0.35,
    4: 0.20,
    5: 0.10,
    6: 0.05,
    7: 0.02,
    8: 0.01,
}
DEPRECIATION_SOURCE = "Gartner IT Asset Valuation Guidelines 2023 + Apple Trade-In"

PREMIUM_KEYWORDS = ["iPhone", "MacBook", "iPad", "ThinkPad", "Surface"]
PREMIUM_RETENTION_BONUS = 0.15


# =============================================================================
# 6. PRODUCTIVITY LOSS MODEL
# =============================================================================
# SOURCE: Microsoft Workplace Analytics Study 2022
PRODUCTIVITY_CONFIG = {
    "optimal_years": 3,
    "degradation_per_year": 0.03,
    "max_degradation": 0.15,
}
PRODUCTIVITY_SOURCE = "Microsoft Workplace Analytics Study 2022"


# =============================================================================
# 7. REFURBISHED PARAMETERS
# =============================================================================
# SOURCE: Apple Environmental Progress Report 2023
REFURB_CONFIG = {
    "co2_reduction_factor": 0.85,
    "price_discount_factor": 0.45,
    "energy_penalty_factor": 0.10,
    "warranty_years": 2,
}
REFURB_SOURCE = "Apple Environmental Progress Report 2023"


# =============================================================================
# 8. URGENCY FRAMEWORK
# =============================================================================
# SOURCE: ITIL v4 Framework - Incident Priority Matrix
URGENCY_CONFIG = {
    "age_critical_years": 5,
    "age_high_years": 4,
    "performance_threshold": 0.70,
    "eol_threshold_months": 6,
}
URGENCY_THRESHOLDS = {"HIGH": 2.0, "MEDIUM": 1.3, "LOW": 0.0}
URGENCY_SOURCE = "ITIL v4 Framework - Incident Priority Matrix"


# =============================================================================
# 9. CARBON GRID FACTORS (Fallback Values)
# =============================================================================
# SOURCE: European Environment Agency 2023 + ElectricityMaps
GRID_CARBON_FACTORS = {
    "FR": {"factor": 0.052, "name": "France"},
    "DE": {"factor": 0.350, "name": "Germany"},
    "UK": {"factor": 0.230, "name": "United Kingdom"},
    "US": {"factor": 0.380, "name": "United States"},
    "CN": {"factor": 0.550, "name": "China"},
    "JP": {"factor": 0.450, "name": "Japan"},
    "IT": {"factor": 0.270, "name": "Italy"},
    "ES": {"factor": 0.210, "name": "Spain"},
    "CH": {"factor": 0.030, "name": "Switzerland"},
    "PL": {"factor": 0.700, "name": "Poland"},
    "HK": {"factor": 0.510, "name": "Hong Kong"},
    "SG": {"factor": 0.408, "name": "Singapore"},
    "AE": {"factor": 0.420, "name": "UAE"},
    "KR": {"factor": 0.460, "name": "South Korea"},
    "AU": {"factor": 0.510, "name": "Australia"},
    "BR": {"factor": 0.070, "name": "Brazil"},
    "MX": {"factor": 0.420, "name": "Mexico"},
    "IN": {"factor": 0.700, "name": "India"},
    "RU": {"factor": 0.310, "name": "Russia"},
    "CA": {"factor": 0.120, "name": "Canada"},
    "NL": {"factor": 0.290, "name": "Netherlands"},
    "BE": {"factor": 0.140, "name": "Belgium"},
    "AT": {"factor": 0.100, "name": "Austria"},
    "SE": {"factor": 0.020, "name": "Sweden"},
    "NO": {"factor": 0.010, "name": "Norway"},
    "DK": {"factor": 0.120, "name": "Denmark"},
    "FI": {"factor": 0.080, "name": "Finland"},
    "PT": {"factor": 0.200, "name": "Portugal"},
    "GR": {"factor": 0.350, "name": "Greece"},
    "CZ": {"factor": 0.380, "name": "Czech Republic"},
    "TW": {"factor": 0.500, "name": "Taiwan"},
    "TH": {"factor": 0.440, "name": "Thailand"},
    "MY": {"factor": 0.550, "name": "Malaysia"},
    "ID": {"factor": 0.650, "name": "Indonesia"},
    "PH": {"factor": 0.500, "name": "Philippines"},
    "VN": {"factor": 0.480, "name": "Vietnam"},
    "ZA": {"factor": 0.850, "name": "South Africa"},
    "EG": {"factor": 0.400, "name": "Egypt"},
    "SA": {"factor": 0.550, "name": "Saudi Arabia"},
    "TR": {"factor": 0.380, "name": "Turkey"},
    "IL": {"factor": 0.450, "name": "Israel"},
    "NZ": {"factor": 0.100, "name": "New Zealand"},
    "CL": {"factor": 0.340, "name": "Chile"},
    "AR": {"factor": 0.300, "name": "Argentina"},
    "CO": {"factor": 0.150, "name": "Colombia"},
    "PE": {"factor": 0.200, "name": "Peru"},
}
DEFAULT_GRID_FACTOR = 0.270
GRID_SOURCE = "European Environment Agency 2023 + ElectricityMaps"


# =============================================================================
# 10. MAISONS (ILLUSTRATIVE ESTIMATES FOR DEMO)
# =============================================================================
# NOTE: These are illustrative estimates based on public information.
# Actual fleet data should be obtained from LVMH IT asset management.
MAISONS = {
    "Louis Vuitton": {
        "category": "Fashion & Leather Goods",
        "estimated_fleet_size": 8500,
        "estimated_avg_age_years": 3.2,
        "primary_regions": ["FR", "CN", "US", "JP"],
    },
    "Christian Dior": {
        "category": "Fashion & Leather Goods",
        "estimated_fleet_size": 6200,
        "estimated_avg_age_years": 3.5,
        "primary_regions": ["FR", "CN", "US", "JP"],
    },
    "Sephora": {
        "category": "Selective Retailing",
        "estimated_fleet_size": 12000,
        "estimated_avg_age_years": 4.1,
        "primary_regions": ["FR", "US", "CN", "IT"],
    },
    "Moët Hennessy": {
        "category": "Wines & Spirits",
        "estimated_fleet_size": 3800,
        "estimated_avg_age_years": 4.5,
        "primary_regions": ["FR", "US", "CN", "UK"],
    },
    "Bulgari": {
        "category": "Watches & Jewelry",
        "estimated_fleet_size": 2100,
        "estimated_avg_age_years": 3.0,
        "primary_regions": ["IT", "CN", "US", "JP"],
    },
    "Tiffany & Co.": {
        "category": "Watches & Jewelry",
        "estimated_fleet_size": 2800,
        "estimated_avg_age_years": 3.8,
        "primary_regions": ["US", "CN", "JP", "UK"],
    },
    "Fendi": {
        "category": "Fashion & Leather Goods",
        "estimated_fleet_size": 1900,
        "estimated_avg_age_years": 3.6,
        "primary_regions": ["IT", "CN", "US", "JP"],
    },
    "Loewe": {
        "category": "Fashion & Leather Goods",
        "estimated_fleet_size": 1200,
        "estimated_avg_age_years": 3.4,
        "primary_regions": ["ES", "CN", "US", "JP"],
    },
    "Celine": {
        "category": "Fashion & Leather Goods",
        "estimated_fleet_size": 1500,
        "estimated_avg_age_years": 3.3,
        "primary_regions": ["FR", "CN", "US", "JP"],
    },
    "Kenzo": {
        "category": "Fashion & Leather Goods",
        "estimated_fleet_size": 900,
        "estimated_avg_age_years": 4.2,
        "primary_regions": ["FR", "JP", "CN", "US"],
    },
    "Rimowa": {
        "category": "Other",
        "estimated_fleet_size": 600,
        "estimated_avg_age_years": 2.8,
        "primary_regions": ["DE", "CN", "US", "JP"],
    },
    "Le Bon Marché": {
        "category": "Selective Retailing",
        "estimated_fleet_size": 1100,
        "estimated_avg_age_years": 4.8,
        "primary_regions": ["FR"],
    },
}
MAISONS_SOURCE = "Illustrative estimates for demonstration purposes"
MAISONS_DISCLAIMER = "These figures are estimates based on public information. Actual data should be obtained from LVMH IT asset management systems."


# =============================================================================
# 11. STRATEGIES
# =============================================================================
STRATEGIES = {
    "baseline": {
        "name": "Baseline",
        "description": "Current 4-year refresh cycle with 100% new device procurement",
        "refresh_years": 4,
        "refurb_rate": 0.0,
        "recovery_rate": 0.0,
        "implementation_cost_factor": 0.0,
    },
    "lifecycle_extension": {
        "name": "Lifecycle Extension",
        "description": "Extend device refresh cycle from 4 to 5 years",
        "refresh_years": 5,
        "refurb_rate": 0.0,
        "recovery_rate": 0.0,
        "implementation_cost_factor": 0.02,
    },
    "circular_procurement": {
        "name": "Circular Procurement",
        "description": "Prioritize refurbished devices for 70% of replacements",
        "refresh_years": 4,
        "refurb_rate": 0.70,
        "recovery_rate": 0.0,
        "implementation_cost_factor": 0.05,
    },
    "asset_recovery": {
        "name": "Asset Recovery",
        "description": "Systematic resale program for all retired devices",
        "refresh_years": 4,
        "refurb_rate": 0.0,
        "recovery_rate": 0.85,
        "implementation_cost_factor": 0.03,
    },
    "combined_optimization": {
        "name": "Combined Optimization",
        "description": "Lifecycle extension + circular procurement + asset recovery",
        "refresh_years": 5,
        "refurb_rate": 0.70,
        "recovery_rate": 0.85,
        "implementation_cost_factor": 0.08,
    },
    "aggressive_transition": {
        "name": "Aggressive Transition",
        "description": "Maximum impact: 6-year cycle, 90% refurbished, full recovery",
        "refresh_years": 6,
        "refurb_rate": 0.90,
        "recovery_rate": 0.95,
        "implementation_cost_factor": 0.12,
    },
}
STRATEGIES_SOURCE = "EcoCycle methodology based on Gartner and Forrester best practices"


# =============================================================================
# 12. UI CONFIGURATION
# =============================================================================
UI_CONFIG = {
    "colors": {
        "background": "#0D0D0D",
        "surface": "#1A1A1A",
        "border": "#2D2D2D",
        "text_primary": "#FFFFFF",
        "text_secondary": "#A0A0A0",
        "accent_gold": "#C9A962",
        "success": "#4A7C59",
        "warning": "#C4A35A",
        "danger": "#8B4049",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_device_names():
    return list(DEVICES.keys())

def get_persona_names():
    return list(PERSONAS.keys())

def get_country_codes():
    return {code: data["name"] for code, data in GRID_CARBON_FACTORS.items()}

def get_maison_names():
    return list(MAISONS.keys())

def get_grid_factor(country_code):
    return GRID_CARBON_FACTORS.get(country_code, {}).get("factor", DEFAULT_GRID_FACTOR)

def get_depreciation_rate(age_years):
    return DEPRECIATION_CURVE.get(int(min(age_years, 8)), 0.01)

def is_premium_device(device_name):
    return any(kw in device_name for kw in PREMIUM_KEYWORDS)

def get_disposal_cost(device_name):
    device = DEVICES.get(device_name, {})
    return DISPOSAL_COST_WITH_DATA if device.get("has_data", True) else DISPOSAL_COST_NO_DATA

def get_all_sources():
    return {
        "Working Hours": HOURS_SOURCE,
        "Electricity Price": PRICE_SOURCE,
        "Personas": PERSONAS_SOURCE,
        "Devices": DEVICES_SOURCE,
        "Disposal Costs": DISPOSAL_SOURCE,
        "Depreciation": DEPRECIATION_SOURCE,
        "Productivity": PRODUCTIVITY_SOURCE,
        "Refurbished": REFURB_SOURCE,
        "Urgency": URGENCY_SOURCE,
        "Grid Factors": GRID_SOURCE,
        "Maisons": MAISONS_SOURCE,
        "Strategies": STRATEGIES_SOURCE,
    }