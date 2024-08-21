from xmlrpc.client import boolean
from numpy import float256
from cacer_simulator.models import parameters
import datetime
from typing import Dict, Tuple

### fixed parameters come from parameters.py

## FUNCTIONS IN COMMON FOR ALL 3 USE CASES


# computation of the regional irradiance given the region
def computation_regional_irradiance(region: str) -> int:
    if region not in parameters.irradiance:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    regional_irradiance = parameters.irradiance[region]
    return regional_irradiance


# computation of the optimal size of PV plant in kw given the annual consumption and the region
def optimal_sizing(
    annual_consumption: float, region: str, percentage_daytime_consum: float
) -> float:
    required_PV_energy = annual_consumption * percentage_daytime_consum
    regional_irradiance = computation_regional_irradiance(region)
    optimal_PV_size = required_PV_energy / (
        regional_irradiance * parameters.efficiency * parameters.loss_factor
    )
    return optimal_PV_size


# computation of the annual production in kWh given the power of the PV plant
def production_estimate(plant_power: float, region: str) -> float:
    regional_irradiance = computation_regional_irradiance(region)
    energy_year = plant_power * regional_irradiance * parameters.loss_factor
    return energy_year


# computation of the installable power in kW given the area in m2
def computation_installable_power(area: float) -> float:
    installable_power = (area / parameters.area_one_PV) * (parameters.power_peak / 1000)
    return installable_power


# computation of intallation costs based on installable power in kw
def cost_estimate(plant_power: float) -> float:
    installation_cost = parameters.kW_cost * plant_power
    return installation_cost


# computation of reducted CO2 based on annual self-consumed energy in kwh
def environmental_benefits(self_consumed_energy: float) -> float:
    reduced_CO2 = self_consumed_energy * parameters.avg_emissions_factor
    return reduced_CO2


# computation of the benefit B (benefit on self consumpted energy)
def economical_benefit_b(
    plant_power: float,
    year: datetime.date,
    plant_enhancement: float,
    region: str,
    self_consumed_energy: float,
) -> float:
    energy_self_consum = self_consumed_energy / 1000  # conversion to MWh
    # Determine the base tariff
    tariff = parameters.ARERA_valorisation
    for power_range, base_tariff in parameters.tariff_dict.items():
        if power_range[0] <= plant_power < power_range[1]:
            tariff = base_tariff + parameters.ARERA_valorisation
            break
    # Tariff increase depending on the area
    if plant_power < 1000 and region in parameters.regional_tariff_increase:
        tariff += parameters.regional_tariff_increase[region]
    benefit = tariff * energy_self_consum
    # Adjust benefit if implant_year is before 16/12/2021
    if year < datetime.date(2021, 12, 16):
        total_power = plant_power + plant_enhancement
        energy_old = energy_self_consum * (plant_power / total_power)
        energy_new = energy_self_consum - energy_old
        benefit_old = energy_old * tariff * 0.3
        benefit_new = energy_new * tariff
        benefit = benefit_new + benefit_old
    return benefit


# estimation of annual self consumed energy in kWh
def estimate_self_consumed_energy(
    annual_consuption: float, percentage_daytime_consum: float, annual_production: float
) -> float:
    diurnal_consum = percentage_daytime_consum * annual_consuption
    energy_self_consump = min(diurnal_consum, annual_production)
    return energy_self_consump


# computation of the difference between the energy producted and the energy consumed in a year in kWh
def energy_difference(energy_self_consump: float, annual_production: float) -> float:
    difference = annual_production - energy_self_consump
    return difference


# computation of the area (m2) necessary to install the optimal plant power (kW)
def computation_optimal_area(optimal_plant_power: float) -> float:
    optimal_area = (optimal_plant_power * parameters.area_one_PV) / (
        parameters.power_peak / 1000
    )
    return optimal_area


## FUNCTION FOR CER AND GROUPS OF SELF CONSUMERS


# computation of benefit A (only for municipalities with less than 5000 inhabitants)
def economical_benefit_a(plant_power: float, inhabitants: boolean) -> float:
    benefit = 0
    if inhabitants == True:
        # Determine the benefit based on the power range
        for power_range, tariff in parameters.tariff_municipality_dict.items():
            if power_range[0] <= plant_power < power_range[1]:
                benefit = tariff * plant_power
                break
    return benefit


# Estimation of the annual consumption in kWh starting from the number and type of members.
# For Groups of self consumers the only typology is appartments.
def consumption_estimation(members: dict) -> float:
    total_consumption = 0
    for member_type, member_count in members.items():
        if member_type in parameters.consumption_rates:
            total_consumption += (
                member_count * parameters.consumption_rates[member_type]
            )
    return total_consumption


## FUNCTION FOR CER


# estimation of the optimal members of a CER based on the annual production of energy in kWh
def optimal_members(energy_year: float) -> Dict[str, int]:
    members = {key: 0 for key in parameters.consumption_rates_diurnal_hours.keys()}
    remaining_overproduction = energy_year
    # Ordina i membri per consumo decrescente
    sorted_members = sorted(
        parameters.consumption_rates_diurnal_hours.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    for member_type, consumption_rates_diurnal_hours in sorted_members:
        if remaining_overproduction <= 0:
            break
        num_members = int(remaining_overproduction // consumption_rates_diurnal_hours)
        members[member_type] = num_members
        remaining_overproduction -= num_members * consumption_rates_diurnal_hours
    return members
