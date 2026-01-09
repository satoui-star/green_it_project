from env_roi.inventory_loader import load_inventory
from env_roi.carbon_factor_loader import load_carbon_factors
from engine.calculator import (
    compute_equipment_co2,
    compute_environmental_roi
)

def main():
    print("=== LOADING INVENTORY ===")
    inventory, lifespan, price = load_inventory()
    print(inventory)

    print("\n=== LOADING CARBON FACTORS ===")
    carbon_factors = load_carbon_factors()
    print(carbon_factors)

    print("\n=== COMPUTING CO2 & ENVIRONMENTAL ROI ===")
    co2_results = compute_equipment_co2(inventory, carbon_factors)

    for item, co2 in co2_results.items():
        roi = compute_environmental_roi(co2)
        print(f"{item}: {co2:.1f} kg CO2 → {roi:.1f} €")

if __name__ == "__main__":
    main()


