from math import inf
import numpy as np
from pydantic import NonNegativeInt, PositiveFloat, validate_call, PositiveInt
import main
import multivector_simulator.common as common
from typing import Literal, Tuple
from cacer_simulator.common import PositiveOrZeroFloat, get_kw_cost
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt


def calculate_mean_over_period(data: np.ndarray, hours: int) -> np.ndarray:
    """
    Calculate the mean value of production or consumption over a period of time.
    Attrs:
        data: array - production or consumption data
        hours: int - number of hours in the period"""

    data_start = data[0:hours]
    for i in range(1, round((len(data) / hours)) - 1):
        data_start = data_start + data[hours * i + 1 : hours * (i + 1) + 1]
    mean_value = data_start / round(len(data) / hours)
    return mean_value


def energy_self_consumed(
    produced_energy: np.ndarray, consumed_energy: np.ndarray
) -> np.ndarray:
    """Calculation of the energy self consumed as the min between producted and consumed energy."""
    self_consumption = np.minimum(produced_energy, consumed_energy)
    return self_consumption


def cost_battery_installation(battery_size: PositiveInt) -> PositiveFloat:
    """Calculation of installation costs for battery (euro).
    Attrs:
    battery_size: PositiveInt - size of the battery in kWh"""
    cost_battery = battery_size * common.COST_INSTALLATION_BATTERY
    return cost_battery


def cost_cogen_trigen_installation(
    cogen_trigen_size: NonNegativeInt, labelCogTrigen: str
) -> PositiveFloat:
    """Calculation of installation costs for cogenerator/trigenerator (euro).
    Attrs:
    cogen_trigen_size: NonNegativeInt - size of the cogenerator or trigenerator in kW
    labelCogTrigen: str - indicating "Cogen" or "Trigen"""
    cost_cogen_trigen = 0
    if labelCogTrigen == "Cogen":
        cogen = common.Trigen_Cogen().Cogenerator()
        cost_cogen_trigen = cogen_trigen_size * cogen.get_kw_cost_cogen(
            cogen_trigen_size
        )
    elif labelCogTrigen == "Trigen":
        trigen = common.Trigen_Cogen().Trigenerator()
        cost_cogen_trigen = cogen_trigen_size * trigen.get_kw_cost_trigen(
            cogen_trigen_size
        )
    return cost_cogen_trigen


def cost_gas_used_cogen_trigen(used_gas: PositiveFloat) -> PositiveFloat:
    """
    Calculation of the cost of the gas used by cogenerator/trigenerator in euro.
    Attrs:
        used_gas: PositiveFloat - quantity of gas used in Smc
    """
    trigen_cogen = common.Trigen_Cogen()
    cost_gas = used_gas * trigen_cogen.COST_GAS_FOR_GEN
    return cost_gas


def cost_PV_installation(PV_size: PositiveInt) -> float:
    """
    Calculation of the cost of the installation of the PV plant in euro.

    Attrs:
        PV_size: PositiveInt - size of the PV plant in kW
    """
    cost_PV = get_kw_cost(PV_size) * PV_size
    return cost_PV


def total_cost_investment(
    PV_size: NonNegativeInt,
    battery_size: NonNegativeInt,
    cogen_trigen_size: NonNegativeInt,
    labelCogTrigen: str,
) -> PositiveFloat:
    """
    Calculation of cost of installation of battery, PV, cogen/trigen in euro.

    Attrs:
        PV_size: NonNegativeInt - size of the PV plant in kW
        battery_size: NonNegativeInt - size of the battery in kW
        cogen_trigen_size: NonNegativeInt - size of the cogenerator or trigenerator in kW
        labelCogTrigen: str - indicating "Cogen" or "Trigen"
    """
    total_cost = (
        cost_PV_installation(PV_size)
        + cost_battery_installation(battery_size)
        + cost_cogen_trigen_installation(cogen_trigen_size, labelCogTrigen)
    )
    return total_cost


def cost_energy_from_grid(energy_from_grid: PositiveOrZeroFloat) -> PositiveOrZeroFloat:
    """
    Calculation of the cost of the energy from the grid in euro.
    Attrs:
        energy_from_grid: PositiveOrZeroFloat - energy from grid in kWh
    """
    cost_grid_energy = energy_from_grid * common.ELECTRIC_ENERGY_PRICE
    return cost_grid_energy


def cogen_trigen_usage_gas(
    cogen_trigen_size: NonNegativeInt, working_hours: NonNegativeInt
) -> PositiveFloat:
    """
    Calculation of the quantity (Smc) of gas used by cogenerator/trigenerator to work for a certain amount of hours working at full capacity.
    Attrs:
        cogen_trigen_size: NonNegativeInt - size of the cogenerator or trigenerator in kW
        working_hours: NonNegativeInt - amount of hours working at full capacity
    """
    trigen_cogen = common.Trigen_Cogen()
    used_gas = working_hours * trigen_cogen.get_gas_quantity_cogen_trigen(
        cogen_trigen_size
    )
    return used_gas


def maintenance_cost_PV(
    PV_size: NonNegativeInt, battery_size: NonNegativeInt
) -> PositiveOrZeroFloat:
    """
    Calculation of the annual cost of the maintenance of the PV plant (with or without battery) in euro.
    """
    if battery_size != 0:
        annually_cost_maintenance_PV = (
            common.MAINTENANCE_COST_PV["with_battery"] * PV_size
        )
    else:
        annually_cost_maintenance_PV = (
            common.MAINTENANCE_COST_PV["no_battery"] * PV_size
        )
    return annually_cost_maintenance_PV


def maintenance_cost_cogen_trigen(
    cogen_trigen_size: NonNegativeInt, LabelCogTrigen: str
) -> PositiveOrZeroFloat:
    """
    Calculation of the annual cost of the maintenance of the cogenerator/trigenerator in euro.
    Attrs:
        cogen_trigen_size: PositiveOrZeroFloat - size of the cogenerator or trigenerator in kW
        labelCogTrigen: str - indicating "Cogen" or "Trigen"

    """
    cost_installation_trigen_cogen = cost_cogen_trigen_installation(
        cogen_trigen_size, LabelCogTrigen
    )
    annually_maintenance_cost_cogen_trigen = (
        common.Trigen_Cogen().MAINTENANCE_COST_PERCENTAGE
        * cost_installation_trigen_cogen
    )
    return annually_maintenance_cost_cogen_trigen


def total_economic_cost(
    annual_electric_energy_from_grid: PositiveOrZeroFloat,
    annual_thermal_energy_from_grid: PositiveOrZeroFloat,
    annually_used_gas: PositiveOrZeroFloat,
    PV_size: NonNegativeInt,
    battery_size: NonNegativeInt,
    cogen_trigen_size: NonNegativeInt,
    labelCogTrigen: str,
) -> PositiveFloat:
    """
    Calculation of total costs over 20years, sum of:
    -installation of battery
    -installation of cogen/trigen
    -installation of PV
    -electric energy from grid
    -thermal energy from grid
    -gas used by cogen/trigen
    -costs of maintenance of PV and cogen/trigen

    Attrs:
        annual_electric_energy_from_grid: PositiveOrZeroFloat - annual electric energy from grid in kWh
        annual_thermal_energy_from_grid: PositiveOrZeroFloat - annual thermal energy from grid in kWh
        annually_used_gas: PositiveOrZeroFloat - annual quantity of gas used in Smc
        PV_size: NonNegativeInt - size of the PV plant in kW
        battery_size: NonNegativeInt - size of the battery in kW
        cogen_trigen_size: NonNegativeInt - size of the cogenerator or trigenerator in kW
        labelCogTrigen: str - indicating "Cogen" or "Trigen"

    Returns:
        PositiveFloat - total costs over 20 years in euro
    """

    cost_electricity_from_grid = (
        annual_electric_energy_from_grid * common.ELECTRIC_ENERGY_PRICE
    )
    cost_electricity_from_grid_actualized = actualization(
        cost_electricity_from_grid, labelCostSaving="Costs"
    ).sum()

    cost_thermal_from_grid = (
        annual_thermal_energy_from_grid * common.THERMAL_ENERGY_PRICE
    )
    cost_thermal_from_grid_actualized = actualization(
        cost_thermal_from_grid, labelCostSaving="Costs"
    ).sum()

    cost_installation_PV = cost_PV_installation(PV_size)
    cost_installation_battery = cost_battery_installation(battery_size)
    cost_installation_trigen_cogen = cost_cogen_trigen_installation(
        cogen_trigen_size, labelCogTrigen
    )

    annually_cost_gas = cost_gas_used_cogen_trigen(annually_used_gas)
    annually_cost_gas_actualized = actualization(
        annually_cost_gas, labelCostSaving="Costs"
    ).sum()

    annually_cost_maintenance_PV = maintenance_cost_PV(PV_size, battery_size)
    cost_maintenance_PV_actualized = actualization(
        annually_cost_maintenance_PV, labelCostSaving="Costs"
    ).sum()

    annually_cost_maintenance_cogen_trigen = maintenance_cost_cogen_trigen(
        cogen_trigen_size, labelCogTrigen
    )
    cost_maintenance_cogen_trigen_actualized = actualization(
        annually_cost_maintenance_cogen_trigen, labelCostSaving="Costs"
    ).sum()
    total_cost = (
        cost_installation_PV
        + cost_installation_battery
        + cost_installation_trigen_cogen
        + (cost_electricity_from_grid_actualized)
        + (cost_thermal_from_grid_actualized)
        + (annually_cost_gas_actualized)
        + (cost_maintenance_cogen_trigen_actualized)
        + (cost_maintenance_PV_actualized)
    )
    return total_cost


def savings_using_implants(
    electric_energy: PositiveOrZeroFloat,
    thermal_energy: PositiveOrZeroFloat,
    refrigeration_energy: PositiveOrZeroFloat,
) -> PositiveOrZeroFloat:
    """
    Calculation of the savings in euro.
    Attrs:
        electric_energy: PositiveOrZeroFloat - electric energy self-consumed in kWh
        thermal_energy: PositiveOrZeroFloat - thermal energy self-consumed in kWh
        refrigeration_energy: PositiveOrZeroFloat - refrigeration energy self-consumed in kWh
    """
    savings = (
        (electric_energy) * common.ELECTRIC_ENERGY_PRICE
        + thermal_energy * common.THERMAL_ENERGY_PRICE
        + refrigeration_energy
        * (
            1 / common.EFFICIENCY_CONDITIONER
        )  # per ogni kwh che un condizionartore consuma, produce N kWh di energia frigorifera
        * common.ELECTRIC_ENERGY_PRICE
    )
    return savings


def savings_in_a_period(savings: PositiveFloat, period: PositiveInt) -> PositiveFloat:
    """Calculation of the savings over a period of time.
    Attrs:
        savings: PositiveFloat - savings in euro
        period: PositiveInt - period in years"""
    savings_period = actualization(savings, period, "Savings").sum()
    return savings_period


def cumulative_costs_savings(
    savings_in_year: PositiveOrZeroFloat,
    initial_investment: PositiveOrZeroFloat,
    costs_in_year: PositiveOrZeroFloat,
) -> pd.DataFrame:
    """
    Calculation of the cumulative costs and savings in which the i-th element represents the cumulative sum of costs(negative)+savings(positive) of the i-th year.
    Attrs:
        savings_in_year: PositiveOrZeroFloat - savings in a year in euro
        initial_investment: PositiveOrZeroFloat - initial investment in euro
        costs_in_year: PositiveOrZeroFloat - costs in a year in euro
    """

    years = common.Optimizer().YEARS
    annual_value = [-initial_investment]
    annual_costs = -actualization(costs_in_year, labelCostSaving="Costs")
    annual_savings = actualization(savings_in_year, labelCostSaving="Savings")
    for i in range(1, years + 1):
        value = annual_value[-1] + annual_costs[i - 1] + annual_savings[i - 1]
        annual_value.append(value)

    df = pd.DataFrame(
        {"Year": np.arange(0, years + 1), "Cumulative value": annual_value}
    )

    return df


def calc_payback_time(df: pd.DataFrame) -> NonNegativeInt | float:
    """
    Calculation of the payback time in years.
    Attrs:
        df: pd.DataFrame - cumulative costs and savings in which the i-th element represents the cumulative sum of costs(negative)+savings(positive) of the i-th year
    """
    if (df["Cumulative value"] > 0).any():
        payback_time = np.where(df["Cumulative value"] > 0)[0][
            0
        ]  # takes first positive value
    else:
        payback_time = float(inf)
    return payback_time


def calculate_cogen_or_trigen_energy_coverage(
    thermal_consumption: np.ndarray,
    refrigerator_consumption: np.ndarray,
    electric_consumption: np.ndarray,
    cogen_or_trigen_size: NonNegativeInt,
    labelCogTrigen: str,
) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray
]:
    """
    Calculation of the annual electric, thermal and refrigeration coverage of consumption from cogen or trigen.

    Attrs:
        thermal_consumption: np.ndarray - annual thermal consumption in kWh
        refrigerator_consumption: np.ndarray - annual refrigerator consumption in kWh
        electric_consumption: np.ndarray - annual electric consumption in kWh
        cogen_or_trigen_size: NonNegativeInt - size of the cogenerator or trigenerator in kW
        labelCogTrigen: str - indicating "Cogen" or "Trigen"

    Returns:
        electric_energy_from_grid: np.ndarray - annual electric energy from grid in kWh. Energy not covered by cogen/trigen
        thermal_energy_from_grid: np.ndarray - annual thermal energy from grid in kWh. Energy not covered by cogen/trigen
        refrigeration_energy_from_grid: np.ndarray - annual refrigerator energy from grid in kWh. Energy not covered by cogen/trigen
        self_consumption_electric_energy_from_cogen_trigen: np.ndarray - annual electric energy self-consumed in kWh
        self_consumption_thermal_energy_from_cogen_trigen: np.ndarray - annual thermal energy self-consumed in kWh
        self_consumption_refrigeration_energy_from_cogen_trigen: np.ndarray - annual refrigerator energy self-consumed in kWh
        available_battery_energy_from_cogen_trigen: np.ndarray - energy not consumed, available to be stored in a battery if present in kWh


    """

    # Calculate the total COGEN/TRIGEN PRODUCTION scaled by its size
    (
        cogen_trigen_electric_production,
        cogen_trigen_thermal_production,
        cogen_trigen_refrigeration_production,
    ) = annual_production_cogen_trigen(cogen_or_trigen_size, labelCogTrigen)

    # INITIALIZE ARRAYS
    electric_energy_from_grid = np.zeros_like(electric_consumption)
    thermal_energy_from_grid = np.zeros_like(thermal_consumption)
    refrigeration_energy_from_grid = np.zeros_like(refrigerator_consumption)
    available_battery_energy_from_cogen_trigen = np.zeros_like(electric_consumption)

    # ENERGY BALANCE
    # electric energy
    excess_electric_energy_cogen_trigen = np.maximum(
        cogen_trigen_electric_production - electric_consumption, 0
    )  ##excess of eletric energy produced by cogen/trigen that can be stored in a battery
    electric_consumption_before_cogen_trigen = electric_consumption.copy()
    ##update the electric consumption subtracting the electric energy produced by cogenerator/trigenerator
    electric_consumption = np.clip(
        electric_consumption - cogen_trigen_electric_production, 0, None
    )
    # thermal energy balance
    thermal_consumption_before_cogen_trigen = thermal_consumption.copy()
    ##update the thermal consumption subtracting the thermal energy produced by cogenerator/trigenerator
    thermal_consumption = np.clip(
        thermal_consumption - cogen_trigen_thermal_production, 0, None
    )
    # refrigeration energy balance
    refrigeration_consumption_before_cogen_trigen = refrigerator_consumption.copy()
    ##update the refrigeration consumption subtracting the refrigeration energy produced by cogenerator/trigenerator
    refrigerator_consumption = np.clip(
        refrigerator_consumption - cogen_trigen_refrigeration_production, 0, None
    )

    # SELF CONSUMPTION
    # electric energy self-consumed
    self_consumption_electric_energy_from_cogen_trigen = (
        electric_consumption_before_cogen_trigen - electric_consumption
    )
    # thermal energy self-consumed
    self_consumption_thermal_energy_from_cogen_trigen = (
        thermal_consumption_before_cogen_trigen - thermal_consumption
    )
    # refrigeration energy self-consumed
    self_consumption_refrigeration_energy_from_cogen_trigen = (
        refrigeration_consumption_before_cogen_trigen - refrigerator_consumption
    )

    # BATTERY
    # Update battery energy with excess electric production
    available_battery_energy_from_cogen_trigen = (
        available_battery_energy_from_cogen_trigen + excess_electric_energy_cogen_trigen
    )

    # ENERGY FROM GRID
    # electric energy taken from the grid (what ramins not covered by cogen/trigen)
    electric_energy_from_grid = electric_consumption
    # thermal energy taken from the grid (what ramins not covered by cogen/trigen)
    thermal_energy_from_grid = thermal_consumption
    # refrigeration energy taken from grid (what ramins not covered by cogen/trigen)
    refrigeration_energy_from_grid = refrigerator_consumption

    return (
        electric_energy_from_grid,
        thermal_energy_from_grid,
        refrigeration_energy_from_grid,
        self_consumption_electric_energy_from_cogen_trigen,
        self_consumption_thermal_energy_from_cogen_trigen,
        self_consumption_refrigeration_energy_from_cogen_trigen,
        available_battery_energy_from_cogen_trigen,
    )


def annual_production_cogen_trigen(
    size_cogen_trigen: NonNegativeInt, labelCogTrigen: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate the electric, thermal, refrigeration production (kWh) based on the size of the cogenerator/trigenerator. Production in one year.
    Attrs:
        size_cogen_trigen: NonNegativeInt - size of the cogenerator/trigenerator in kW
        labelCogTrigen: str - flag "Cogen" or "Trigen"

    Returns:
        electric_production: np.ndarray - annual electric production in kWh by cogen/trigen
        thermal_production: np.ndarray - annual thermal production in kWh by cogen/trigen
        refrigerator_production: np.ndarray - annual refrigerator production in kWh by cogen/trigen
    """
    # intialize vectors containing all zeros
    electric_production = np.zeros(common.HOURS_OF_YEAR)
    thermal_production = np.zeros(common.HOURS_OF_YEAR)
    refrigerator_production = np.zeros(common.HOURS_OF_YEAR)
    # update vectors with actual production
    # cogenerator
    if labelCogTrigen == "Cogen":
        cogen = common.Trigen_Cogen().Cogenerator()
        electric_production[:] = size_cogen_trigen * cogen.ELECTRIC_EFFICIENCY_COGEN
        thermal_production[:] = size_cogen_trigen * cogen.THERMAL_EFFICIENCY_COGEN
    # trigenerator
    elif labelCogTrigen == "Trigen":
        trigen = common.Trigen_Cogen().Trigenerator()
        electric_production[:] = size_cogen_trigen * trigen.ELECTRIC_EFFICIENCY_TRIGEN
        thermal_production[:] = size_cogen_trigen * trigen.THERMAL_EFFICIENCY_TRIGEN
        refrigerator_production[:] = (
            size_cogen_trigen * trigen.REFRIGERATION_EFFICIENCY_TRIGEN
        )
    return electric_production, thermal_production, refrigerator_production


def calculation_pv_production(pv_size) -> np.ndarray:
    """Annual PV production in kWh.
    Attrs:
        pv_size: PositiveInt - size of the PV plant in kW
    """
    pv_production = common.pv_production_hourly * pv_size
    return pv_production


def determination_electric_coverage_year_PV_battery(
    electric_consumption: np.ndarray,
    available_battery_energy_from_cogen: np.ndarray,
    pv_size: PositiveInt,
    battery_size: PositiveInt,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Determines the annual electric coverage provided by the PV system, battery storage,
    and the energy drawn from the grid (in kWh).

    Args:
        electric_consumption (np.ndarray): Array representing the electric consumption per hour over the year (kWh).
        available_battery_energy_from_cogen (np.ndarray): Initial energy available from the cogenerator to be stored in the battery (kWh).
        pv_size (PositiveInt): Installed capacity of the PV system (kW).
        battery_size (PositiveInt): Battery storage capacity (kWh).

    Returns:
        Tuple containing:
            - energy_from_grid (np.ndarray): Energy taken from the grid to meet the consumption (kWh).
            - self_consumed_energy_battery_pv (np.ndarray): Battery energy consumed, stored from PV (kWh).
            - self_consumed_energy_battery_cogen (np.ndarray): Battery energy consumed, stored from cogeneration (kWh).
            - self_consumption_electric_energy_from_pv (np.ndarray): Energy directly consumed from PV (kWh).
    """

    # PRODUCTION
    # From PV
    pv_production = calculation_pv_production(pv_size)

    # INITIALIZE ARRAYS
    energy_from_grid = np.zeros_like(electric_consumption)
    # the energy available for battery is initialize to the energy in excess from the cogenerator/trigenerator
    available_battery_energy = np.clip(
        available_battery_energy_from_cogen, 0, battery_size
    )
    available_battery_energy_from_pv = np.zeros_like(electric_consumption)

    # ENERGY BALANCE
    # from PV
    excess_energy_pv = np.maximum(pv_production - electric_consumption, 0)
    electric_consumption_before_pv = electric_consumption.copy()
    ##update electric consumption subtracting electric energy produced by PV
    electric_consumption = np.clip(electric_consumption - pv_production, 0, None)

    # SELF CONSUMPTION ELECTRIC ENERGY
    # from PV
    self_consumption_electric_energy_from_pv = (
        electric_consumption_before_pv - electric_consumption
    )

    # save of energy available for battery coming from PV
    available_battery_energy_before_pv = np.clip(excess_energy_pv, 0, battery_size)
    # Update battery energy with excess PV production
    available_battery_energy = np.clip(
        available_battery_energy + excess_energy_pv, 0, battery_size
    )
    available_battery_energy_from_pv = (
        available_battery_energy - available_battery_energy_before_pv
    )

    # Energy balance with battery storage
    electric_consumption_before_battery = electric_consumption.copy()
    ##update electric consumption subtracting energy from battery
    electric_consumption = np.clip(
        electric_consumption - available_battery_energy, 0, None
    )

    # Split battery consumption between PV and cogenerator sources to know which energy is from
    battery_usage_ratio = np.divide(
        available_battery_energy_from_pv,
        available_battery_energy,
        out=np.zeros_like(available_battery_energy),
        where=available_battery_energy != 0,
    )
    # self-consumed energy in battery charged with PV excess
    self_consumed_energy_battery_pv = (
        electric_consumption_before_battery - electric_consumption
    ) * battery_usage_ratio
    # self-consumed energy in battery charged with cogen/trigen excess
    self_consumed_energy_battery_cogen = (
        electric_consumption_before_battery - electric_consumption
    ) * (1 - battery_usage_ratio)

    # ENERGY FROM GRID (energy not covered with PV or battery)
    energy_from_grid = electric_consumption

    return (
        energy_from_grid,
        self_consumed_energy_battery_pv,
        self_consumed_energy_battery_cogen,
        self_consumption_electric_energy_from_pv,
    )


def objective_function(
    x,
    electric_consumption,
    thermal_consumption,
    refrigerator_consumption,
    labelCogTrigen,
):
    """
    Determination of the objective function to be minimized.
    Attrs:
    electric_consumption: array - electric yearly consumption in kWh
    thermal_consumption: array - thermal yearly consumption in kWh
    refrigerator_consumption: array - refrigerator yearly consumption in kWh
    labelCogTrigen: str - indicating "Cogen" or "Trigen"

    Returns:
    objective_function - function to be minimized
    """

    PV_size, battery_size, cogen_or_trigen_size = x  # parameters to be determined

    # calculation of the electric, thermal and refrigerator coverage per year covered by cogen/trigen

    (
        electric_energy_from_grid_cogen,
        thermal_energy_from_grid,
        refrigeration_energy_from_grid,
        self_consumption_electric_energy_from_cogen_trigen,
        self_consumption_thermal_energy_from_cogen_trigen,
        self_consumption_refrigeration_energy_from_cogen_trigen,
        available_battery_energy_from_cogen_trigen,
    ) = calculate_cogen_or_trigen_energy_coverage(
        thermal_consumption,
        refrigerator_consumption,
        electric_consumption,
        cogen_or_trigen_size,
        labelCogTrigen,
    )

    # UPDATE THE ELECTRIC CONSUMPTION BY SUBTRACTING THE ELECTRIC ENERGY PRODUCED BY COGEN/TRIGEN
    electric_consumption = np.clip(
        electric_consumption - self_consumption_electric_energy_from_cogen_trigen,
        0,
        None,
    )

    # CALCULATION OF THE ELECTRIC COVERAGE PER YEAR COVERED BY PV AND BATTERY
    (
        energy_from_grid_PV_battery,
        energy_battery_pv,
        energy_battery_cogen,
        electric_energy_from_pv,
    ) = determination_electric_coverage_year_PV_battery(
        electric_consumption,
        available_battery_energy_from_cogen_trigen,
        PV_size,
        battery_size,
    )

    # COSTS
    # energy from grid
    ##electric (considering even refrigeration)
    total_electric_energy_from_grid = (
        np.nansum(
            energy_from_grid_PV_battery
        )  # electric energy from grid after adding PV and battery
        + np.nansum(
            electric_energy_from_grid_cogen
        )  # electric energy from grid after adding cogen/trigen
        + np.nansum(
            refrigeration_energy_from_grid
            * (
                1 / common.EFFICIENCY_CONDITIONER
            )  # per ogni kwh che un condizionartore consuma, produce N kWh di energia frigorifera
        )  # electric energy from grid after adding cogen/trigen for refrigeration
    )
    # thermal
    total_thermal_energy_from_grid = np.nansum(thermal_energy_from_grid)

    # electric production by cogen/trigen
    (
        electric_production_cogen,
        thermal_production_cogen,
        refrigeration_production_cogen,
    ) = annual_production_cogen_trigen(cogen_or_trigen_size, labelCogTrigen)
    # number of hours in which the cogen works at full capacity
    working_hours = np.count_nonzero(electric_production_cogen)
    # quantity of gas in Smc used annyally by cogen
    annually_used_gas = cogen_trigen_usage_gas(cogen_or_trigen_size, working_hours)
    # total costs
    total_cost = total_economic_cost(
        total_electric_energy_from_grid,
        total_thermal_energy_from_grid,
        annually_used_gas,
        PV_size,
        battery_size,
        cogen_or_trigen_size,
        labelCogTrigen,
    )

    # Final objective function: balance between minimizing costs and maximizing coverage
    objective_function = total_cost
    return objective_function


def optimizer(
    electric_consumption: np.ndarray,
    thermal_consumption: np.ndarray,
    refrigerator_consumption: np.ndarray,
    labelCogTrigen: str,
) -> tuple[NonNegativeInt, NonNegativeInt, NonNegativeInt]:
    """Calculation of the best sizes of PV, battery and cogen/trigen

    Attrs:
    electric_consumption: np.ndarray - electric annual consumptions in kWh
    thermal_consumption: np.ndarray - thermal annual consumptions in kWh
    refrigerator_consumption: np.ndarray - refrigerator annual consumption in kWh
    labelCogTrigen: str - label indicating "Cogen" or "Trigen"

    Returns:
    Tuple cotaining:
    -PV_size: NonNegativeInt - best pv size in KW
    -battery_size: NonNegativeInt - best battery size in kW
    -cogen_trigen_size : NonNegativeInt - best cogen/trigen size in kW

    """

    initial_guess = (
        common.Optimizer().INITIAL_GUESS
    )  # Guess for PV size and battery size
    result = minimize(
        objective_function,
        initial_guess,
        args=(
            electric_consumption,
            thermal_consumption,
            refrigerator_consumption,
            labelCogTrigen,
        ),
        method="SLSQP",
        bounds=common.Optimizer().BOUNDS,
    )
    PV_size, battery_size, cogen_trigen_size = result.x
    print("Optimization success:", result.success)
    print("Optimization message:", result.message)
    return (
        round(PV_size),
        round(battery_size),
        round(cogen_trigen_size),
    )


def actualization(
    annual_cost: PositiveFloat,
    years=common.Optimizer().YEARS,
    labelCostSaving: str = "Costs",
) -> np.ndarray:
    """
    Calculation of the value of a cost or of a saving over a period of time (years) based on "formula del valore attuale", in euro.
    Attrs:
        annual_cost: PositiveFloat - annual cost in euro
        labelCostSaving: str - label indicating "Savings" or "Costs"

    Returns:
        actualized_cost: np.ndarray - actualized costs/saving in euro. i-th element is the actualized cost/saving for the i-th year in euro.
    """
    discount_rate = common.Optimizer().DISCOUNT_RATE
    if labelCostSaving == "Savings":
        actualized_cost = np.array(
            [annual_cost / ((1 + discount_rate) ** i) for i in range(1, years + 1)]
        )
    else:
        actualized_cost = np.array(
            [annual_cost * ((1 + discount_rate) ** i) for i in range(1, years + 1)]
        )
    return actualized_cost
