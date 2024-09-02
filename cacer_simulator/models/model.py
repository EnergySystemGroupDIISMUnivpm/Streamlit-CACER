import datetime

from pydantic import PositiveFloat, validate_call

import cacer_simulator.common as common


@validate_call
def computation_regional_irradiance(region: common.RegionType) -> int:
    """
    computation of the regional irradiance given the region.
    """
    if region not in common.IRRADIANCE:
        raise ValueError(
            f"Regione '{region}' non trovata nel dizionario di irradiance."
        )
    regional_irradiance = common.IRRADIANCE[region]
    return regional_irradiance


@validate_call
def optimal_sizing(
    annual_consumption: PositiveFloat,
    region: common.RegionType,
    percentage_daytime_consum: common.PercentageType,
) -> float:
    """
    Computation of the optimal size of PV plant in kw given the annual consumption and the region.

    Attrs:
        annual_consumption: PositiveFloat - consumed energy in kWh
        region: RegionType - region in which there is the PV plant
        percentage_daytime_consum: PercentageType - percentage of the total consumption referring to how much of the total consumption is
        consumed during the daytime (i want it from 0 to 1)

    """
    required_PV_energy = annual_consumption * percentage_daytime_consum
    regional_irradiance = computation_regional_irradiance(region)
    optimal_PV_size = required_PV_energy / (
        regional_irradiance * common.EFFICIENCY * common.LOSS_FACTOR
    )
    return optimal_PV_size


@validate_call
def production_estimate(
    plant_power: PositiveFloat,
    region: common.RegionType,
) -> float:
    """
    Computation of the annual production in kWh given the power of the PV plant.

    Attrs:
        plant_power: PositiveFloat - power of PV plant in KW
        region: RegionType - region in which there is the PV plant

    """
    regional_irradiance = computation_regional_irradiance(region)
    energy_year = plant_power * regional_irradiance * common.LOSS_FACTOR
    return energy_year


@validate_call
def computation_installable_power(area: PositiveFloat) -> float:
    """
    computation of the installable power in kW given the area.

    Attrs:
        area: PositiveFloat - area in m2
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


@validate_call
def environmental_benefits(self_consumed_energy: PositiveFloat) -> float:
    """
    Computation of reduced CO2 emissions based on annual self-consumed energy.

    Attrs:
        self_consumed_energy: Positivefloat - self-consumed energy in kWh
    """
    reduced_CO2 = self_consumed_energy * common.AVG_EMISSIONS_FACTOR
    return reduced_CO2


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
        plant_power: PositiveFloat - power of PV plant in kW
        year: datetime.date - year of construction of the PV
        plant_enhancement: PositiveOrZeroFloat - enhancement of the PV plant in kW
        region: RegionType - region
        self_consumed_energy: PositiveFloat - self-consumed energy in kWh

    Usage:

    ```
    result = economical_benefit_b(
        1000,
        datetime.date(2021, 12, 16),
        0,
        "Lazio",
        300,
    )

    assert result == 3.0
    ```
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
    """
    Computation of the annual self-consumed energy in kWh.

    Attrs:
        annual_consumption: PositiveFloat - consumed energy in kWh
        percentage_daytime_consum: PercentageType - percentage of the total consumption referring to how much of the total consumption is during the daytime
        annual_production: PositiveFloat - annual production in kWh
    """
    diurnal_consum = percentage_daytime_consum * annual_consuption
    energy_self_consump = min(diurnal_consum, annual_production)
    return energy_self_consump


@validate_call
def energy_difference(
    energy_self_consump: PositiveFloat,
    annual_production: PositiveFloat,
) -> float:
    """
    Computation of the difference between the energy producted and the energy consumed in a year in kWh.

    Attrs:
        energy_self_consump: PositiveFloat - energy consumed in kWh
        annual_production: PositiveFloat - energy produced in kWh
    """
    difference = annual_production - energy_self_consump
    return difference


@validate_call
def computation_optimal_area(optimal_plant_power: PositiveFloat) -> float:
    """
    Computation of the area (m2) necessary to install the optimal plant power (kW).

    Attrs:
        optimal_plant_power: PositiveFloat - power of PV plant in kW
    """
    optimal_area = (optimal_plant_power * common.AREA_ONE_PV) / (
        common.POWER_PEAK / 1000
    )
    return optimal_area


def presence_of_overproduction_or_underproduction(
    difference_produc_consum: float, region: common.RegionType
) -> str:
    """
    Computation of the fact that it is necessary to increase the PV power, to include other members to share with energy or consumptions are almost equal to production.

    Attrs:
        difference_produc_consum: float - difference between production and consumption in kWh. Can be even negative.
        region: RegionType - region
    """
    energy_one_pv = production_estimate(common.POWER_PEAK / 1000, region)
    if difference_produc_consum > 0:
        return "Overproduction"
    elif -energy_one_pv < difference_produc_consum <= 0:
        return "Optimal"
    else:
        return "Underproduction"


## FUNCTION FOR CER AND GROUPS OF SELF CONSUMERS


@validate_call
def economical_benefit_a(
    plant_power: PositiveFloat,
) -> float:
    """
    Computation of benefit A (only for municipalities with less than 5000 inhabitants).

    Attrs:
        plant_power: PositiveFloat - power of PV plant in kW
        inhabitants: bool - True if the municipality has less than 5000 inhabitants.
    """

    # Determine the benefit based on the power range
    benefit = common.Tariff().get_tariff_municipality(plant_power) * plant_power
    return benefit


@validate_call
def consumption_estimation(members: common.MembersWithValues) -> int:
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


@validate_call
def percentage_daytime_consumption_estimation(
    members: common.MembersWithValues,
) -> PositiveFloat:
    """
    Estimation of the percentage of the annual consumption related to how much energy is consumed during daytime,
    starting from the number and type of members.

    For Groups of self consumers the only typology is appartments.

    Attrs:

    members: MembersWithValues - number and type of members.
    """
    total_percentage = 0
    total_members_count = 0
    for member_type, member_count in members.items():
        percentage = common.ConsumptionByMember().get_consumption_percentage(
            member_type
        )
        total_percentage += member_count * percentage  # type: ignore
        total_members_count += member_count  # type: ignore
    total_percentage = total_percentage / 100
    if total_members_count > 0:
        return round(total_percentage / total_members_count, 2)
    else:
        return 0.0


## FUNCTION FOR CER


@validate_call(validate_return=True)
def optimal_members(energy_year: PositiveFloat) -> common.MembersWithValues:
    """
    estimation of the optimal members of a CER based on the annual production of energy in kWh.

    Attrs:
        energy_year: PositiveFloat - annual production in kWh.

    Usage:

    ```
    result = optimal_members(1000)
    assert result == {
        "bar": 0,
        "appartamenti": 10,
        "pmi": 0,
        "hotel": 0,
        "ristoranti": 0,
    }
    ```
    """
    members = {key: 0 for key in common.ConsumptionByMember().members}
    remaining_overproduction = energy_year

    # Get sorted consumption rates by member type
    sorted_consumption = common.ConsumptionByMember().get_sorted_diurnal(reverse=True)

    # Find the member with the minimum consumption rate
    min_consumption_member = min(sorted_consumption, key=lambda x: x[1])
    min_member_type = min_consumption_member[0]

    for member_type, consumption_rates_diurnal_hours in sorted_consumption:
        if remaining_overproduction <= 0:
            break

        num_members = int(remaining_overproduction // consumption_rates_diurnal_hours)
        members[member_type] = num_members
        remaining_overproduction -= num_members * consumption_rates_diurnal_hours

    # If remaining energy is still greater than zero but not enough for a full member, assign it to the min consumption member
    if remaining_overproduction > 0:
        members[min_member_type] += 1

    return members  # type: ignore
