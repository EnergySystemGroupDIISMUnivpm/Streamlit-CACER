import pandas as pd
from typing import Dict, Tuple, Union
from pathlib import Path
import datetime
import parameters

PATH_RESOURCES = Path(__file__).parents[1] / "resources"


# COMPUTATION OF ANNUAL PRODUCTION DEPENDING ON REGION (to know the irradiance) AND AVAILABLE AREA
def computation_annual_production_from_area(
    area_PV: int | float, region: str
) -> Tuple[float, float]:
    if region not in parameters.Irradiance:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    irradiance = parameters.Irradiance[region]
    PV_yield = (parameters.Power_peak / 1000) / parameters.Area_one_PV  # kWp/m2
    Energy_year = (
        area_PV * irradiance * PV_yield * parameters.loss_factor
    )  # energy in kWh/year formula from https://www.sunbasedata.com/blog/how-to-calculate-solar-panel-output
    P_installable = (area_PV / parameters.Area_one_PV) * (parameters.Power_peak/1000)
    return Energy_year, P_installable

def computation_annual_production_from_power(power:int|float,region:str)->int|float:
    if region not in parameters.Irradiance:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    irradiance = parameters.Irradiance[region]
    Energy_year=power*irradiance*parameters.loss_factor
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
    if region not in parameters.Irradiance:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    PV_dimension = required_PV_energy / (parameters.Irradiance[region] * parameters.efficiency * parameters.loss_factor)
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
    energy_self_consum = energy_self_consum / 1000  # conversion to MWh
    # Determine the base tariff
    tariff = parameters.ARERA_valorisation
    for power_range, base_tariff in parameters.tariff_dict.items():
        if power_range[0] <= implant_power < power_range[1]:
            tariff = base_tariff + parameters.ARERA_valorisation
            break
    # Tariff increase depending on the area
    if implant_power < 1000 and region in parameters.regional_tariff_increase:
        tariff += parameters.regional_tariff_increase[region]
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
    # Determine the benefit based on the power range
    benefit = 0
    for power_range, tariff in parameters.tariff_municipality_dict.items():
        if power_range[0] <= implant_power < power_range[1]:
            benefit = tariff * implant_power
            break
    return benefit


# Reduced CO2
def computation_reduced_CO2(
    energy_self_consum: int | float,
) -> int | float:  # energy in kWh
    reduced_CO2 = energy_self_consum * parameters.avg_emissions_factor
    return reduced_CO2


# saving of Prosumer
def savings(energy_self_consumed: int | float) -> int | float:
    savings = energy_self_consumed * parameters.energy_price
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
    members = {key: 0 for key in parameters.consumption_rates.keys()}
    remaining_overproduction = overproduction

    # Ordina i membri per consumo decrescente
    sorted_members = sorted(parameters.consumption_rates.items(), key=lambda x: x[1], reverse=True)

    for member_type, consumption_rate in sorted_members:
        if remaining_overproduction <= 0:
            break
        num_members = int(remaining_overproduction // consumption_rate)
        members[member_type] = num_members
        remaining_overproduction -= num_members * consumption_rate

    return members
