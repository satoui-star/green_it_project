# DATABASE OF SPECS
# Sources: LVMH Hackathon Data (Excel Screenshots) + ADEME Benchmarks

EQUIPMENT_DB = {
    "Laptop": {
        "price_new": 1000,          # Average cost
        "lifespan_months": 60,      # 5 years
        "co2_manufacturing": 250,   # kgCO2e embedded
        "power_watts": 0.03,        # 30W usage
    },
    "Smartphone": {
        "price_new": 500,
        "lifespan_months": 48,      # 4 years
        "co2_manufacturing": 60,
        "power_watts": 0.005,
    },
    "Screen": {
        "price_new": 2000,          # High-end LVMH Monitor
        "lifespan_months": 72,      # 6 years
        "co2_manufacturing": 350,
        "power_watts": 0.16,
    },
    "Tablet": {
        "price_new": 500,
        "lifespan_months": 60,
        "co2_manufacturing": 150,
        "power_watts": 0.01,
    },
    "Switch/Router": {
        "price_new": 250,
        "lifespan_months": 72,
        "co2_manufacturing": 100,
        "power_watts": 0.05,
    },
    "Landline phone": {
        "price_new": 350,
        "lifespan_months": 96,      # 8 years
        "co2_manufacturing": 40,
        "power_watts": 0.003,
    },
    "Meeting room screen": {
        "price_new": 3000,
        "lifespan_months": 84,      # 7 years
        "co2_manufacturing": 800,   # Large footprint
        "power_watts": 0.30,
    },
    # --- REFURBISHED OPTIONS ---
    "Refurbished smartphone": {
        "price_new": 1,             # Symbolic cost
        "lifespan_months": 36,
        "co2_manufacturing": 10,    # Low impact (parts only)
        "power_watts": 0.005,
    },
    "Refurbished screen": {
        "price_new": 800,
        "lifespan_months": 72,
        "co2_manufacturing": 20,    # Transport + Cleaning only
        "power_watts": 0.16,
    }
}