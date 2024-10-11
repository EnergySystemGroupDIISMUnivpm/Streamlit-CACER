import numpy as np
from pydantic import NonNegativeInt, PositiveFloat, validate_call, PositiveInt
import multivector_simulator.common as common
from typing import Tuple
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


def cost_cogen_installation(cogen_size: PositiveInt) -> PositiveFloat:
    """Calculation of installation costs for cogenerator (euro).
    Attrs:
    cogen_size: PositiveInt - size of the cogenerator in kW"""
    cost_cogen = cogen_size * common.COST_INSTALLATION_COGEN
    return cost_cogen


def cost_gas_used_cogen(used_gas: PositiveFloat) -> PositiveFloat:
    """
    Calculation of the cost of the gas used by cogenerator in euro.
    Attrs:
        used_gas: PositiveFloat - quantity of gas used in Smc
    """
    cost_gas = used_gas * common.COST_GAS_FOR_GEN
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
    PV_size: NonNegativeInt, battery_size: NonNegativeInt, cogen_size: NonNegativeInt
) -> PositiveFloat:
    """
    Calculation of the total cost of the investment (installation of PV, battery and/or cogenerator) in euro.
    Attrs:
        PV_size: NonNegativeInt - size of the PV plant in kW
        battery_size: NonNegativeInt - size of the battery in kWh
        cogen_size: NonNegativeInt - size of the cogenerator in kW"""
    total_cost = (
        cost_PV_installation(PV_size)
        + cost_battery_installation(battery_size)
        + cost_cogen_installation(cogen_size)
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


def cogen_usage_gas(
    cogen_size: PositiveInt, working_hours: PositiveInt
) -> PositiveFloat:
    """
    Calculation of the quantity (Smc) of gas used by cogenerator to work for a certain amount of hours working at full capacity.
    """
    used_gas = cogen_size * working_hours * common.CONSUMPTION_COGEN_HOUR
    return used_gas


def calculate_production_CO2_cogen(quantity_gas: PositiveFloat) -> PositiveOrZeroFloat:
    """
    Calculation of how much CO2 (kg) is produced by using the cogenerator.
    Attrs:
        quantity_gas: PositiveFloat - quantity of gas used in Smc"""
    CO2 = (
        quantity_gas
        * common.AVG_EMISSIONS_FACTOR_THERMAL
        * common.COGEN_CONVERSION_FACTOR
    )
    return CO2


def total_economic_cost_PV_battery_grid(
    annual_energy_from_grid: PositiveFloat,
    PV_size: PositiveInt,
    battery_size: PositiveInt,
):
    """
    Calculation of the total economical cost of the installation and use of PV, installation and use of battery and usage of energy from the grid over the years.

    Attrs:
        annual_energy_from_grid: float - energy from grid in kWh
        PV_size: PositiveInt - size of the PV plant in kW
        battery_size: PositiveInt - size of the battery in kWh
        years: PositiveInt - number of years over wich calculate the economical cost. If not setted is equal to 20.

    """
    years = common.Optimizer().YEARS
    cost_electricity_from_grid = (
        np.nansum(annual_energy_from_grid) * common.ELECTRIC_ENERGY_PRICE
    )
    cost_installation_PV = cost_PV_installation(PV_size)
    cost_installation_battery = cost_battery_installation(battery_size)
    total_cost = (
        cost_installation_PV
        + cost_installation_battery
        + (cost_electricity_from_grid * years)
    )
    return total_cost


def savings_using_implants(
    electric_energy: PositiveOrZeroFloat,
    thermal_energy: PositiveOrZeroFloat,
) -> PositiveOrZeroFloat:
    """
    Calculation of the savings in euro.
    Attrs:
        electric_energy: PositiveOrZeroFloat - electric energy self-consumed in kWh
        thermal_energy: PositiveOrZeroFloat - thermal energy self-consumed in kWh
    """
    savings = (
        electric_energy
    ) * common.ELECTRIC_ENERGY_PRICE + thermal_energy * common.THERMAL_ENERGY_PRICE
    return savings


def savings_in_a_period(savings: PositiveFloat, period: PositiveInt) -> PositiveFloat:
    """Calculation of the savings over a period of time.
    Attrs:
        savings: PositiveFloat - savings in euro
        period: PositiveInt - period in years"""
    savings_period = savings * period
    return savings_period


def calc_payback_time(
    savings: PositiveOrZeroFloat, investment: PositiveOrZeroFloat
) -> NonNegativeInt:
    """
    Calculation of the payback time in years.
    Attrs:
        savings: PositiveOrZeroFloat - savings in euro of each year, obtained by the usage of implants.
        investment: PositiveOrZeroFloat - investment in euro
    """
    payback_time = savings / investment
    payback_time = round(payback_time)
    return payback_time


def calculate_cogen_size_optimized(
    thermal_consumption: np.ndarray, thermal_efficiency=common.THERMAL_EFFICIENCY_COGEN
) -> int:
    """
    Calculation of the best size in kW of cogenerator based on the thermal consumption.
    For more info regarding the used method see: https://industriale.viessmann.it/blog/dimensionare-cogeneratore-massima-efficienza
    """
    threshold = common.Optimizer().COGEN_COVERAGE
    # Sort the heat consumption in decreasing order
    sorted_consumption = np.sort(thermal_consumption)[::-1]

    # Power required to cover the threshold of the time
    threshold_hours = int(threshold * len(thermal_consumption))
    size_cogen = sorted_consumption[threshold_hours] / thermal_efficiency
    return round(size_cogen)


def unitary_production_cogen_optimized(size_cogen: int) -> Tuple[float, float]:
    """
    Calculate the electric and thermal unitary production based on the size of the cogenerator. Production in one hour.
    Attrs:
        size_cogen: int - size of the cogenerator in kW
    """
    electric_production = size_cogen * common.ELECTRIC_EFFICIENCY_COGEN
    thermal_production = size_cogen * common.THERMAL_EFFICIENCY_COGEN
    return electric_production, thermal_production


def annual_energy_cogen(
    electric_consumption, thermal_consumption
) -> tuple[np.ndarray, np.ndarray]:
    """
    Annual production of electric and thermal energy from cogenerator.
    """
    threshold = common.Optimizer().COGEN_COVERAGE
    size_cogen = calculate_cogen_size_optimized(
        thermal_consumption,
        thermal_efficiency=common.THERMAL_EFFICIENCY_COGEN,
    )
    electric_energy_cogen_hourly, thermal_energy_cogen_hourly = (
        unitary_production_cogen_optimized(size_cogen)
    )

    # Precompute the cogenerator production across the entire year
    electric_energy_cogen = np.full_like(
        electric_consumption, electric_energy_cogen_hourly
    )

    # Precompute the cogenerator production across the entire year
    thermal_energy_cogen = np.full_like(
        thermal_consumption, thermal_energy_cogen_hourly
    )
    return electric_energy_cogen, thermal_energy_cogen


def calculation_pv_production(pv_size):
    """Annual PV production in kWh.
    Attrs:
        pv_size: PositiveInt - size of the PV plant in kW
    """
    pv_production = common.pv_production_hourly * pv_size
    return pv_production


def determination_electric_coverage_year(
    electric_consumption: np.ndarray,
    available_battery_energy_from_cogen: np.ndarray,
    pv_size: PositiveInt,
    battery_size: PositiveInt,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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
            - energy_covered (np.ndarray): Total energy consumption covered by the PV and battery (kWh).
            - energy_from_grid (np.ndarray): Energy taken from the grid to meet the consumption (kWh).
            - self_consumed_energy_battery_pv (np.ndarray): Battery energy consumed, stored from PV (kWh).
            - self_consumed_energy_battery_cogen (np.ndarray): Battery energy consumed, stored from cogeneration (kWh).
            - self_consumption_electric_energy_from_pv (np.ndarray): Energy directly consumed from PV (kWh).
    """

    # Calculate the total PV production scaled by its size
    pv_production = calculation_pv_production(pv_size)

    # Initialize arrays for energy tracking
    energy_from_grid = np.zeros_like(electric_consumption)
    energy_covered = np.zeros_like(electric_consumption)
    available_battery_energy = np.clip(
        available_battery_energy_from_cogen, 0, battery_size
    )
    available_battery_energy_from_pv = np.zeros_like(electric_consumption)

    # Energy balance with PV production
    excess_energy_pv = np.maximum(pv_production - electric_consumption, 0)
    electric_consumption_before_pv = electric_consumption.copy()
    electric_consumption = np.clip(electric_consumption - pv_production, 0, None)

    # Energy directly consumed from PV
    self_consumption_electric_energy_from_pv = (
        electric_consumption_before_pv - electric_consumption
    )

    # Update battery energy with excess PV production
    available_battery_energy = np.clip(
        available_battery_energy + excess_energy_pv, 0, battery_size
    )
    available_battery_energy_from_pv = (
        available_battery_energy - available_battery_energy_from_cogen
    )

    # Energy balance with battery storage
    electric_consumption_before_battery = electric_consumption.copy()
    electric_consumption = np.clip(
        electric_consumption - available_battery_energy, 0, None
    )

    # Split battery consumption between PV and cogenerator sources
    battery_usage_ratio = np.divide(
        available_battery_energy_from_pv,
        available_battery_energy,
        out=np.zeros_like(available_battery_energy),
        where=available_battery_energy != 0,
    )
    self_consumed_energy_battery_pv = (
        electric_consumption_before_battery - electric_consumption
    ) * battery_usage_ratio
    self_consumed_energy_battery_cogen = (
        electric_consumption_before_battery - electric_consumption
    ) * (1 - battery_usage_ratio)

    # Energy taken from the grid
    energy_from_grid = electric_consumption

    # Total energy coverage
    energy_covered = electric_consumption_before_pv - energy_from_grid

    return (
        energy_covered,
        energy_from_grid,
        self_consumed_energy_battery_pv,
        self_consumed_energy_battery_cogen,
        self_consumption_electric_energy_from_pv,
    )


def electric_self_consumption_from_cogen(
    electric_energy_cogen: np.ndarray, electric_consumption: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Quantity of electric energy produced by cogen self-consumed and quantity of still available (kWh).
    Attrs:
        electric_energy_cogen: array - energy produced by cogen in kWh
        electric_consumption: array - electric yearly consumption in kWh

    """
    # energy from cogenerator

    excess_energy_cogen = np.where(
        electric_energy_cogen - electric_consumption > 0,
        electric_energy_cogen - electric_consumption,
        0,
    )
    electric_consumption = np.clip(
        electric_consumption - electric_energy_cogen, 0, None
    )
    return electric_consumption, excess_energy_cogen


def objective_function(x, electric_consumption, available_energy_battery):
    """
    Determination of the objective function to be minimized.
    Attrs:
    electric_consumption: array - electric yearly consumption in kWh
    available_energy_battery: array - energy available at the beginning to be stored in battery in kWh
    """

    PV_size, battery_size = x  # parameters to be determined

    # CALCULATION OF THE ELECTRIC COVERAGE PER YEAR COVERED BY PV AND BATTERY

    (
        energy_covered,
        energy_from_grid,
        energy_battery_pv,
        energy_battery_cogen,
        electric_energy_from_pv,
    ) = determination_electric_coverage_year(
        electric_consumption,
        available_energy_battery,
        PV_size,
        battery_size,
    )

    # Percentage of electric consumption coverage
    percentage_electric_coverage = np.nansum(energy_covered) / np.nansum(
        electric_consumption
    )

    # COSTS
    total_energy_from_grid = np.nansum(energy_from_grid)
    total_cost = total_economic_cost_PV_battery_grid(
        total_energy_from_grid, PV_size, battery_size
    )

    # Final objective function: balance between minimizing costs and maximizing coverage
    alpha = 0.6
    objective_function = (1 - alpha) * total_cost - alpha * percentage_electric_coverage
    return objective_function


def optimizer(
    electric_consumption, thermal_consumption
) -> Tuple[int, int, np.ndarray, np.ndarray]:
    electric_energy_production_cogen, thermal_energy_production_cogen = (
        annual_energy_cogen(electric_consumption, thermal_consumption)
    )
    electric_consumption_before_cogen = electric_consumption
    electric_consumption, available_energy_battery_cogen = (
        electric_self_consumption_from_cogen(
            electric_energy_production_cogen, electric_consumption
        )
    )
    self_consumption_electric_cogen = (
        electric_consumption_before_cogen - electric_consumption
    )
    # available_energy_battery = np.zeros_like(electric_consumption)
    initial_guess = (
        common.Optimizer().INITIAL_GUESS
    )  # Guess for PV size and battery size
    result = minimize(
        objective_function,
        initial_guess,
        args=(
            electric_consumption,
            available_energy_battery_cogen,
        ),
        bounds=common.Optimizer().BOUNDS,  # Bounds for PV size and battery size
    )
    PV_size, battery_size = result.x
    return (
        round(PV_size),
        round(battery_size),
        available_energy_battery_cogen,
        self_consumption_electric_cogen,
    )
