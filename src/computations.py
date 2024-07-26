import pandas as pd
from typing import Dict, Tuple, Union
from pathlib import Path
import datetime

PATH_RESOURCES = Path(__file__).parents[1] / "resources"

# mean values of irradiance for each region (kW/m2)
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
Area_one_PV = 1.7*1.1 # area for 1 PV of Power_peak Wp in m2
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
    P_installable = (area_PV / Area_one_PV) * (Power_peak/1000)
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
def incentive_self_consumption(
    energy_self_consum: Union[int, float],
    implant_power: Union[int, float],
    implant_year: Union[datetime.date, None],
    boosting_power: int,
    region: str
) -> Union[int, float]:
    ARERA_valorisation = 8  # valorisation of ARERA, generally around 8 euro/MWh
    energy_self_consum = energy_self_consum / 1000  # conversion to MWh
    # Tariff definitions using a dictionary
    tariff_dict = {
        (0, 200): 120,
        (200, 600): 110,
        (600, 1000): 100,
    }
    # Determine the base tariff
    tariff = ARERA_valorisation
    for power_range, base_tariff in tariff_dict.items():
        if power_range[0] <= implant_power < power_range[1]:
            tariff = base_tariff + ARERA_valorisation
            break
    # Tariff increase depending on the area
    regional_tariff_increase = {
        "Lazio": 4, "Marche": 4, "Toscana": 4, "Umbria": 4, "Abruzzo": 4,
        "Emilia-Romagna": 10, "Friuli-Venezia Giulia": 10, "Liguria": 10,
        "Lombardia": 10, "Piemonte": 10, "Veneto": 10,
        "Trentino-Alto Adige": 10, "Valle d'Aosta": 10,
    }
    if implant_power < 1000 and region in regional_tariff_increase:
        tariff += regional_tariff_increase[region]
    benefit = tariff * energy_self_consum
    # Adjust benefit if implant_year is before 16/12/2021
    if implant_year is not None and implant_year < datetime.date(2021, 12, 16):
        total_power = implant_power + boosting_power
        energy_old = energy_self_consum * (implant_power / total_power)
        energy_new = energy_self_consum - energy_old
        benefit_old = energy_old * tariff * 0.3
        benefit_new = energy_new * tariff
        benefit = benefit_new + benefit_old
    return benefit


# incentive on CER and Groups of self-consumers in municipalities with < 5000 inhabitants
def incentive_municipality(implant_power: int | float) -> int | float:
    # Define the mapping of power ranges to tariffs
    tariff_dict = {
        (0, 20): 1500,
        (20, 200): 1200,
        (200, 600): 1100,
        (600, float('inf')): 1050,
    }
    # Determine the benefit based on the power range
    benefit = 0
    for power_range, tariff in tariff_dict.items():
        if power_range[0] <= implant_power < power_range[1]:
            benefit = tariff * implant_power
            break
    return benefit


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
