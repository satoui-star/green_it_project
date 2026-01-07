from src.env_roi.inventory_loader import load_inventory
from src.env_roi.carbon_factor_loader import load_carbon_factors

print("Loading inventory...")
inventory, lifespan, price = load_inventory()
print("Inventory:", inventory)
print("Lifespan:", lifespan)
print("Price:", price)

print("\nLoading carbon factors...")
carbon_factors = load_carbon_factors()
print("Carbon factors:", carbon_factors)

