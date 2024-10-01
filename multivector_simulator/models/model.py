import numpy as np
from pydantic import PositiveFloat, validate_call, PositiveInt
import multivector_simulator.common as common
from typing import Tuple
from cacer_simulator.common import get_kw_cost
import pandas as pd
from scipy.optimize import minimize


def cost_PV_installation(PV_size: PositiveInt) -> float:
    """
    Calculation of the cost of the installation of the PV plant in euro.

    Attrs:
        PV_size: PositiveInt - size of the PV plant in kW
    """
    cost_PV = get_kw_cost(PV_size) * PV_size
    return cost_PV


def calculate_cogen_size_optimized(
    thermal_consumption: np.array, threshold: float, thermal_efficiency: float
) -> int:
    """
    Calculation of the best size in kW of cogenerator based on the thermal consumption.
    """
    # Sort the heat consumption in decreasing order
    sorted_consumption = np.sort(thermal_consumption)[::-1]

    # Power required to cover the threshold of the time
    threshold_hours = int(threshold * len(thermal_consumption))
    size_cogen = sorted_consumption[threshold_hours] / thermal_efficiency
    return round(size_cogen)


def production_cogen_optimized(size_cogen: int) -> Tuple[float, float]:
    """
    Calculate the electric and thermal hourly production based on the size of the cogenerator.
    """
    electric_production = size_cogen * common.ELECTRIC_EFFICIENCY_COGEN
    thermal_production = size_cogen * common.THERMAL_EFFICIENCY_COGEN
    return electric_production, thermal_production


def cost_function_optimized(
    x, electric_consumption, thermal_consumption, pv_production_hourly
):
    PV_size, battery_size = x

    # Precompute PV production scaled by size
    pv_production = pv_production_hourly * PV_size

    # COGENERATOR
    threshold = 0.8
    size_cogen = calculate_cogen_size_optimized(
        thermal_consumption,
        threshold,
        thermal_efficiency=common.THERMAL_EFFICIENCY_COGEN,
    )
    electric_energy_cogen_hourly, thermal_energy_cogen_hourly = (
        production_cogen_optimized(size_cogen)
    )

    # Precompute the cogenerator production across the entire year
    electric_energy_cogen = np.full_like(
        electric_consumption, electric_energy_cogen_hourly
    )

    # Initialize arrays for tracking energy
    energy_from_grid = np.zeros_like(electric_consumption)
    energy_covered = np.zeros_like(electric_consumption)
    aviable_battery_energy = np.zeros_like(electric_consumption)

    # Calculate available energy at each hour
    excess_energy_pv = np.clip(pv_production - electric_consumption, 0, None)
    excess_energy_cogen = np.clip(electric_energy_cogen - electric_consumption, 0, None)

    # Total available energy for battery charging
    energy_excess_total = excess_energy_pv + excess_energy_cogen
    aviable_battery_energy = np.minimum(np.cumsum(energy_excess_total), battery_size)

    # Energy that is covered by PV, cogenerator, and battery
    energy_from_pv_cogen = np.minimum(
        electric_consumption, pv_production + electric_energy_cogen
    )
    remaining_energy = np.clip(electric_consumption - energy_from_pv_cogen, 0, None)
    energy_from_battery = np.minimum(remaining_energy, aviable_battery_energy)

    # Energy from the grid is the energy still needed after PV, cogenerator, and battery
    energy_from_grid = remaining_energy - energy_from_battery

    # Coverage of consumption
    energy_covered = electric_consumption - energy_from_grid

    # COSTS
    years = 20
    cost_electricity_from_grid = np.sum(energy_from_grid) * common.ELECTRIC_ENERGY_PRICE
    cost_installation_PV = cost_PV_installation(PV_size)
    cost_installation_battery = battery_size * common.COST_INSTALLATION_BATTERY

    total_cost = (
        cost_installation_PV
        + cost_installation_battery
        + (cost_electricity_from_grid * years)
    )

    # Percentage of electric consumption coverage
    percentage_electric_coverage = np.sum(energy_covered) / np.sum(electric_consumption)

    # Final objective function: balance between minimizing costs and maximizing coverage
    alpha = 0.8
    objective_function = (1 - alpha) * total_cost - alpha * percentage_electric_coverage
    return objective_function


def optimizer(electric_consumption, thermal_consumption, pv_production_hourly):
    initial_guess = [10, 0]  # Guess for PV size and battery size
    result = minimize(
        cost_function_optimized,
        initial_guess,
        args=(electric_consumption, thermal_consumption, pv_production_hourly),
        bounds=[(0, 1000), (0, 10)],  # Bounds for PV size and battery size
    )
    PV_size, battery_size = result.x
    return PV_size, battery_size


def test_optimizer():
    test_data = pd.read_csv(
        "././resources/Dati_Simulati_di_Consumi_Elettrici_e_Termici.csv"
    )
    thermal_consumption = test_data["Consumo_Termico_kWh"].to_numpy()
    electric_consumption = test_data["Consumo_Elettrico_kWh"].to_numpy()

    # Simulated PV production per hour (you can replace it with real data if available)
    pv_production_hourly = pd.read_csv("././resources/PV_data.csv", header=None)[
        2
    ].to_numpy()

    PV_size, battery_size = optimizer(
        electric_consumption, thermal_consumption, pv_production_hourly
    )
    print(f"Optimal PV size: {PV_size}, Optimal battery size: {battery_size}")

    __import__("ipdb").set_trace()  # Breakpoint for debugging


test_optimizer()
