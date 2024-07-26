from typing import Dict, Tuple, Union

regions=[
    "Abruzzo",
    "Basilicata",
    "Calabria",
    "Campania",
    "Emilia-Romagna",
    "Friuli-Venezia Giulia",
    "Lazio",
    "Liguria",
    "Lombardia",
    "Marche",
    "Molise",
    "Piemonte",
    "Puglia",
    "Sardegna",
    "Sicilia",
    "Trentino-Alto Adige",
    "Toscana",
    "Umbria",
    "Valle d'Aosta",
    "Veneto"
]

# mean values of irradiance for each region (kW/m2)
irradiance_values = [
    1575,  # Abruzzo
    1603,  # Basilicata
    1677,  # Calabria
    1611,  # Campania
    1477,  # Emilia-Romagna
    1365,  # Friuli-Venezia Giulia
    1632,  # Lazio
    1500,  # Liguria
    1433,  # Lombardia
    1504,  # Marche
    1568,  # Molise
    1454,  # Piemonte
    1633,  # Puglia
    1714,  # Sardegna
    1786,  # Sicilia
    1390,  # Trentino-Alto Adige
    1548,  # Toscana
    1541,  # Umbria
    1502,  # Valle d'Aosta
    1424   # Veneto
]
#dictionary with the irradiance values
Irradiance = dict(zip(regions, irradiance_values))

# Annual consumption data by member type in kWh
consumption_rates: Dict[str, int] = {
    "bar": 8000,  # kWh consumption from 10 to 15 per year per bar
    "appartamenti": 600,  
    "piccolone e medie imprese": 25000,  
    "hotel": 30000,  
    "ristoranti": 10000,  
}


loss_factor = 0.8  # to take into account losses in the system, such as those due to the inverter, wiring, dust on the panels ecc. 
efficiency = 0.2  # efficinecy of PV.
Power_peak = 300  # Wp of one PV pannel
Area_one_PV = 1.7*1.1 # area for 1 PV with power peak of Power_peak
energy_price = 0.25  # 0.25 euro/kW, price to install 1kW of PV
kW_cost = 1000  # cost of PV panels for kW, euro

options_for_daily_percentage_time = ["Molto", "Mediamente", "Poco"]
percentage_values = [0.75, 0.50, 0.25]
percentage_dict = dict(zip(options_for_daily_percentage_time, percentage_values))

#INCENTIVES
ARERA_valorisation = 10  # valorisation of ARERA
# Tariff definitions acconrding to implant power
tariff_dict = {
        (0, 200): 120, #implant power < 200, incetive is maximum 120 euro/MWh
        (200, 600): 110,
        (600, 1000): 100,
    }
#tariff increase basing on Area
regional_tariff_increase = {
        "Lazio": 4, "Marche": 4, "Toscana": 4, "Umbria": 4, "Abruzzo": 4,
        "Emilia-Romagna": 10, "Friuli-Venezia Giulia": 10, "Liguria": 10,
        "Lombardia": 10, "Piemonte": 10, "Veneto": 10,
        "Trentino-Alto Adige": 10, "Valle d'Aosta": 10,
    }
#tariff depending on ihabitants 
tariff_municipality_dict = {
        (0, 20): 1500, #implant <20kWp incentive=1500euro for kW
        (20, 200): 1200,
        (200, 600): 1100,
        (600, float('inf')): 1050,
    }

avg_emissions_factor = 0.309  # how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
