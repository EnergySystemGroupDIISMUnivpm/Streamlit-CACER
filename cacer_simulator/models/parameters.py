from typing import Dict, Tuple, Union

regions = [
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
    "Veneto",
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
    1424,  # Veneto
]
# dictionary with the irradiance values
irradiance: dict = dict(zip(regions, irradiance_values))

# average loss factor to take into account losses in the system, such as those due to the inverter, wiring, dust on the panels ecc.
loss_factor: float = 0.8

# efficiency of an average PV
efficiency: float = 0.2

# power of one singular PV pannel in W
power_peak = 300

# area of 1 single pannel in m2 with the power defined as power peak
area_one_PV = 1.7 * 1.1

# cost of 1kW of PV in euro
kW_cost = 2000

# how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
avg_emissions_factor = 0.309

# INCENTIVES
ARERA_valorisation = 10  # valorisation of ARERA

# Tariff definitions acconrding to implant power
tariff_dict = {
    (0, 200): 120,  # implant power < 200, incetive is maximum 120 euro/MWh
    (200, 600): 110,
    (600, 1000): 100,
}
# tariff increase basing on Region
regional_tariff_increase = {
    "Lazio": 4,
    "Marche": 4,
    "Toscana": 4,
    "Umbria": 4,
    "Abruzzo": 4,
    "Emilia-Romagna": 10,
    "Friuli-Venezia Giulia": 10,
    "Liguria": 10,
    "Lombardia": 10,
    "Piemonte": 10,
    "Veneto": 10,
    "Trentino-Alto Adige": 10,
    "Valle d'Aosta": 10,
}
# tariff depending on ihabitants
tariff_municipality_dict = {
    (0, 20): 1500,  # implant <20kWp incentive=1500euro for kW
    (20, 200): 1200,
    (200, 600): 1100,
    (600, float("inf")): 1050,
}

# avg annual consumptions during 10 to 15 (central hours of the day) in kWh.
consumption_rates_diurnal_hours: Dict[str, int] = {
    "bar": 8000,
    "appartamenti": 100,
    "piccole e medie imprese": 25000,
    "hotel": 30000,
    "ristoranti": 10000,
}

# avg annual consumptions in kWh
consumption_rates: Dict[str, int] = {
    "bar": 26000,
    "appartamenti": 2000,
    "piccole e medie imprese": 25000,
    "hotel": 700000,
    "ristoranti": 26000,
}
