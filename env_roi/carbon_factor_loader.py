import pandas as pd

def load_carbon_factors(path="assets/Carbon emissions per equipement.csv"):
    """
    Charge les facteurs d'émissions et de consommation par type d'équipement.
    """
    df = pd.read_csv(path)
    # On crée des dictionnaires avec 'equipment_type' comme clé
    factors = df.set_index('equipment_type')['mfg_kgco2e'].to_dict()
    power_factors = df.set_index('equipment_type')['power_watts'].to_dict()
    
    return factors, power_factors
