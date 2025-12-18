import pandas as pd

#Getting the csv file in the github
def load_inventory(path="assets/Original_data_ROI_calculation.csv"):

    df = pd.read_csv(path)

    inventory = {}
    lifespan = {}
    price = {}

    for _, row in df.iterrows():
        category = row["Category"]
        item = row["Item"]
        value = row["Value"]

        if category == "Inventory":
            inventory[item] = value
        elif category == "Lifespan":
            lifespan[item] = value  # months
        elif category == "Price":
            price[item] = value     # euros

    return inventory, lifespan, price

