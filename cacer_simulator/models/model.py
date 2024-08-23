import datetime

from pydantic import PositiveFloat, validate_call

import cacer_simulator.common as common

# TODO: Put function comments into docstrings. Remember to add examples or unit of measurements if required by the function


@validate_call
def computation_regional_irradiance(region: common.RegionType) -> int:
    """
    computation of the regional irradiance given the region
    """
    if region not in common.IRRADIANCE:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    regional_irradiance = common.IRRADIANCE[region]
    return regional_irradiance


# computation of the optimal size of PV plant in kw given the annual consumption and the region
@validate_call
def optimal_sizing(
    annual_consumption: PositiveFloat,
    region: common.RegionType,
    percentage_daytime_consum: common.PercentageType,
) -> float:
    required_PV_energy = annual_consumption * percentage_daytime_consum
    regional_irradiance = computation_regional_irradiance(region)
    optimal_PV_size = required_PV_energy / (
        regional_irradiance * common.EFFICIENCY * common.LOSS_FACTOR
    )
    return optimal_PV_size


# computation of the annual production in kWh given the power of the PV plant
@validate_call
def production_estimate(
    plant_power: PositiveFloat,
    region: common.RegionType,
) -> float:
    regional_irradiance = computation_regional_irradiance(region)
    energy_year = plant_power * regional_irradiance * common.LOSS_FACTOR
    return energy_year


@validate_call
def computation_installable_power(area: PositiveFloat) -> float:
    """
    computation of the installable power in kW given the area in m2
    """
    installable_power = (area / common.AREA_ONE_PV) * (common.POWER_PEAK / 1000)
    return installable_power


@validate_call
def cost_estimate(plant_power: PositiveFloat) -> float:
    """
    Computation of intallation costs based on installable power in kw

    Attrs:
        installable_power: float - installable power in kW
    """
    installation_cost = common.KW_COST * plant_power
    return installation_cost


# computation of reducted CO2 based on annual self-consumed energy in kwh
@validate_call
def environmental_benefits(self_consumed_energy: PositiveFloat) -> float:
    reduced_CO2 = self_consumed_energy * common.AVG_EMISSIONS_FACTOR
    return reduced_CO2


# computation of the benefit B (benefit on self consumpted energy)
@validate_call
def economical_benefit_b(
    plant_power: PositiveFloat,
    year: datetime.date,
    plant_enhancement: common.PositiveOrZeroFloat,
    region: common.RegionType,
    self_consumed_energy: PositiveFloat,
) -> float:
    """
    Calculates the economic benefit on self consumption type B

    Attrs:
        consumed_energy: float - consumed energy in kWh
    """
    energy_self_consum = self_consumed_energy / 1000  # conversion to MWh
    # Determine the base tariff
    tariff = common.Tariff().get_tariff(plant_power) + common.ARERA_VALORISATION

    # Tariff increase depending on the area
    if plant_power < 1000 and region in common.REGIONAL_TARIFF_INCREASE:
        tariff += common.REGIONAL_TARIFF_INCREASE[region]

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
@validate_call
def estimate_self_consumed_energy(
    annual_consuption: PositiveFloat,
    percentage_daytime_consum: common.PercentageType,
    annual_production: PositiveFloat,
) -> float:
    diurnal_consum = percentage_daytime_consum * annual_consuption
    energy_self_consump = min(diurnal_consum, annual_production)
    return energy_self_consump


# computation of the difference between the energy producted and the energy consumed in a year in kWh
@validate_call
def energy_difference(
    energy_self_consump: PositiveFloat,
    annual_production: PositiveFloat,
) -> float:
    difference = annual_production - energy_self_consump
    return difference


# computation of the area (m2) necessary to install the optimal plant power (kW)
@validate_call
def computation_optimal_area(optimal_plant_power: PositiveFloat) -> float:
    optimal_area = (optimal_plant_power * common.AREA_ONE_PV) / (
        common.POWER_PEAK / 1000
    )
    return optimal_area


## FUNCTION FOR CER AND GROUPS OF SELF CONSUMERS


# computation of benefit A (only for municipalities with less than 5000 inhabitants)
@validate_call
def economical_benefit_a(
    plant_power: PositiveFloat,
    inhabitants: bool = False,
) -> float:
    benefit = 0
    if inhabitants == True:
        # Determine the benefit based on the power range
        benefit = common.Tariff().get_tariff_municipality(plant_power) * plant_power
    return benefit


@validate_call
def consumption_estimation(members: common.MembersWithValues) -> int :
    """
    Estimation of the annual consumption in kWh starting from the number and type of members.

    For Groups of self consumers the only typology is appartments.

    Usage:

    ```
    result = consumption_estimation(
        {
            "bar": 0,
            "appartamenti": 10,
            "pmi": 0,
            "hotel": 0,
            "ristoranti": 0,
        }
    )
    assert result == 20_000
    ```
    """
    total_consumption = 0
    for member_type, member_count in members.items():
        total_consumption += (  # type: ignore
            member_count
            * common.ConsumptionByMember().get_consumption_value(member_type)
        )
    return total_consumption


## FUNCTION FOR CER


@validate_call(validate_return=True)
def optimal_members(energy_year: float) -> common.MembersWithValues:
    """
    estimation of the optimal members of a CER based on the annual production of energy in kWh
    """
    members = {key: 0 for key in common.ConsumptionByMember().members}
    remaining_overproduction = energy_year

    for (
        member_type,
        consumption_rates_diurnal_hours,
    ) in common.ConsumptionByMember().get_sorted_diurnal(reverse=True):
        if remaining_overproduction <= 0:
            break
        num_members = int(remaining_overproduction // consumption_rates_diurnal_hours)
        members[member_type] = num_members
        remaining_overproduction -= num_members * consumption_rates_diurnal_hours

    return members  # type: ignore
