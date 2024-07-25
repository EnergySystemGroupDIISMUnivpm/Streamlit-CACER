import pandas as pd
from typing import Dict, Tuple
from pathlib import Path

PATH_RESOURCES = Path(__file__).parents[1] / "resources"

# mean values of irradiance for each region (kWh/m2)
Irradiance = {
    "Abruzzo": 1575,
    "Basilicata": 1603,
    "Calabria": 1677,
    "Campania": 1611,
    "Emilia-Romagna": 1477,
    "Friuli-Venezia Giulia": 1365,
    "Lazio": 1632,
    "Liguria": 1500,
    "Lombardia": 1433,
    "Marche": 1504,
    "Molise": 1568,
    "Piemonte": 1454,
    "Puglia": 1633,
    "Sardegna": 1714,
    "Sicilia": 1786,
    "Trentino-Alto Adige": 1390,
    "Toscana": 1548,
    "Umbria": 1541,
    "Valle d'Aosta": 1502,
    "Veneto": 1424,
}

# Dati di consumo annuali per tipologia di membri in kWh
consumption_rates: Dict[str, int] = {
    "bar": 8000,  # consumi kWh dalle 10 alle 15 per anno per bar
    "appartamenti": 600,  # consumi kWh dalle 10 alle 15 per anno per cittadino
    "piccolone e medie imprese": 25000,  # consumi kWh dalle 10 alle 15 per anno per PMI
    "hotel": 30000,  # consumi kWh dalle 10 alle 15 per anno per Hotel
    "ristoranti": 10000,  # consumi kWh dalle 10 alle 15 per anno per hotel
}


loss_factor = 0.8  # to take into account losses in the system, such as those due to the inverter, wiring, dust on the panels ecc. It can vary
efficiency = 0.2  # efficinecy of PV. It can vary
Power_peak = 300  # Wp of one PV
Area_one_PV = 1.6  # area for 1 PV of Power_peak Wp in m2
energy_price = 0.25  # 0.25 euro/kWh


# COMPUTATION OF ANNUAL PRODUCTION DEPENDING ON REGION (to know the irradiance) AND AVAILABLE AREA
def computation_annual_production_from_area(
    area_PV: int | float, region: str
) -> Tuple[float, float]:
    if region not in Irradiance:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    irradiance = Irradiance[region]
    PV_yield = (Power_peak / 1000) / Area_one_PV  # kWp/m2
    Energy_year = (
        area_PV * irradiance * PV_yield * loss_factor
    )  # energy in kWh/year formula from https://www.sunbasedata.com/blog/how-to-calculate-solar-panel-output
    P_installable = (area_PV / Area_one_PV) * Power_peak
    return Energy_year, P_installable

def computation_annual_production_from_power(power:int|float,region:str)->int|float:
    if region not in Irradiance:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    irradiance = Irradiance[region]
    Energy_year=power*irradiance*loss_factor
    return Energy_year


# computation of intallation costs based on installable power
def computation_installation_cost(P_installable: float) -> float:
    kW_cost = 1000  # cost of PV panels for kW, euro
    installation_cost = kW_cost * P_installable
    return installation_cost


# computation optimal PV dimension based on annual consumption and region (region necessary to know the irradiance)
def computation_optimal_dimension(
    annual_consumption: int | float, region: str, percentage_daytime_consum:float
) -> int | float:
    required_PV_energy = annual_consumption * percentage_daytime_consum
    if region not in Irradiance:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    PV_dimension = required_PV_energy / (Irradiance[region] * efficiency * loss_factor)
    return PV_dimension


##INCENTIVES
  #incentive on self-consumed energy as defined in decreto MASE 07/12/2023
def incentive_self_consumption(energy_self_consum:int|float,implant_power:int|float,region:str)->int|float: #energy and implant power in kWh,kW
   ARERA_valorisation=8 #valorisation of ARERA, it can vary, generally is around 8 euro/MWh. 
   energy_self_consum=energy_self_consum/1000 #conversion in MWh
   #tariff definition
   if implant_power<200:
    tariff=120 + ARERA_valorisation #max of tariff with power <200 KW
   elif implant_power<600:
    tariff=110 + ARERA_valorisation #max of tariff with power <600 KW
   elif implant_power<1000:
    tariff=100 + ARERA_valorisation #max of tariff with power <600 KW
   else:
      tariff=ARERA_valorisation
    #tariff increase depending on the area
   if implant_power<1000: 
    if region in ["Lazio","Marche","Toscana","Umbria","Abruzzo"]:
        tariff=tariff+4 
    elif region in ["Emilia-Romagna","Friuli-Venezia Giulia","Liguria","Lombardia","Piemonte","Veneto","Trentino-Alto Adige","Valle d'Aosta"]:
        tariff=tariff+10
   benefit=tariff*energy_self_consum 
   return int(round(benefit))


# incentive on CER and Groups of self-consumers in municipalities with < 5000 inhabitants
def incentive_municipality(
    implant_power: int | float,
) -> int | float:  # implant power in kW
    if implant_power < 20:  # power < 20kW
        benefit = 1500 * implant_power
    elif implant_power < 200:  # power < 200kW
        benefit = 1200 * implant_power
    elif implant_power < 600:  # power < 600kW
        benefit = 1100 * implant_power
    else:
        benefit = 1050 * implant_power  # power >600kW
    return int(round(benefit))


# Reduced CO2
def computation_reduced_CO2(
    energy_self_consum: int | float,
) -> int | float:  # energy in kWh
    avg_emissions_factor = 0.309  # how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
    reduced_CO2 = energy_self_consum * avg_emissions_factor
    return reduced_CO2


# saving of Prosumer
def savings(energy_self_consumed: int | float) -> int | float:
    savings = energy_self_consumed * energy_price
    return savings


def computation_self_consump(
    annual_consum: int | float, percentage_daily_consump: float, annual_production: int | float
) -> int | float:
    diurnal_consum=percentage_daily_consump*annual_consum
    self_consump=min(diurnal_consum,annual_production)
    return self_consump

# computation of the fact that there is or not overproduction on average yearly values
def comp_overproduction(
    production: int | float, self_consumption: int | float
) -> int | float:
    overproduction = production - self_consumption
    return overproduction


# function that computes the number and typology of members of CER
def find_optimal_members(overproduction: int) -> Dict[str, int]:
    """
    Determina il numero ideale e la tipologia di membri per massimizzare il consumo dell'overproduction.

    :param overproduction: Energia sovraprodotta in kWh
    :param consumption_rates: Dizionario con i consumi annuali in kWh per ogni tipologia di membri
    :return: Dizionario con il numero di membri per ogni tipologia
    """
    members = {key: 0 for key in consumption_rates.keys()}
    remaining_overproduction = overproduction

    # Ordina i membri per consumo decrescente
    sorted_members = sorted(consumption_rates.items(), key=lambda x: x[1], reverse=True)

    for member_type, consumption_rate in sorted_members:
        if remaining_overproduction <= 0:
            break
        num_members = int(remaining_overproduction // consumption_rate)
        members[member_type] = num_members
        remaining_overproduction -= num_members * consumption_rate

    return members
