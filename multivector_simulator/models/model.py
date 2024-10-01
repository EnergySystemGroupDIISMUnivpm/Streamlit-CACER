import numpy as np
from pydantic import PositiveFloat, validate_call, PositiveInt
import multivector_simulator.common as common
from typing import Tuple
from cacer_simulator.common import get_kw_cost
import pandas as pd
from scipy.optimize import minimize


def calculate_cogen_size(
    thermal_cunsumption: np.array,
    threshold: PositiveFloat,
    thermal_efficiency: PositiveFloat,
) -> PositiveInt:
    """
    Calculation of the best size in kW of cogenerator based on the thermal consumption.
    Formula refers to https://industriale.viessmann.it/blog/dimensionare-cogeneratore-massima-efficienza

    Attrs:
        termal_cunsumption: np.array - array of the termal consumption in kWh
        threshold: float - percentage of the numeber of hours of the year in which the cogenerator works at full capacity without having excess of power.
        termal_efficiency: float - efficiency of the cogenerator
    """
    # Sort the heat consumption in decreasing order
    consumo_sorted = np.sort(thermal_cunsumption)[::-1]

    # Power required to cover the threshold of the time (e.g. 6800 hours if it is 0.8)
    threshold_hours = round(threshold * len(thermal_cunsumption))
    size_cogen = consumo_sorted[threshold_hours] / thermal_efficiency
    size_cogen = round(size_cogen)
    return size_cogen


def production_cogen(size_cogen: PositiveInt) -> Tuple[PositiveFloat, PositiveFloat]:
    """
    Calculation of electric and thermal hourly production based on the size of the cogenerator in kWh.

    Attrs:
        size_cogen: PositiveInt - size of the cogenerator in kW
    """
    electric_production = size_cogen * common.ELECTRIC_EFFICIENCY_COGEN
    thermal_production = size_cogen * common.THERMAL_EFFICIENCY_COGEN
    return electric_production, thermal_production


def cost_PV_installation(PV_size: PositiveInt) -> float:
    """
    Calculation of the cost of the installation of the PV plant in euro.

    Attrs:
        PV_size: PositiveInt - size of the PV plant in kW
    """
    cost_PV = get_kw_cost(PV_size) * PV_size
    return cost_PV


def cost_function(x, electric_consumption, thermal_consumption):
    PV_size, battery_size = x  # parameters to be estimated

    # BATTERY
    # Energy stored in the battery
    energy_battery = np.zeros_like(electric_consumption)
    aviable_battery_energy = 0  # Available battery capacity at any given time

    # COGENERATOR
    # energy produced by the cogenerator
    thereshold = 0.8
    size_cogen = calculate_cogen_size(
        thermal_consumption,
        thereshold,
        thermal_efficiency=common.THERMAL_EFFICIENCY_COGEN,
    )
    [electric_energy_cogen_each_hour, thermal_energy_cogen_each_hour] = (
        production_cogen(size_cogen)
    )
    electric_energy_cogen = np.full_like(
        electric_consumption, electric_energy_cogen_each_hour
    )  # production of electric energy given by the cogenerator during the year

    # GRID
    energy_from_grid = 0

    energy_covered = 0

    # hourly electricity consumption coverage
    for i in range(len(electric_consumption)):
        requested_energy = electric_consumption[i]
        initial_requested_energy = requested_energy

        # from cogenerator
        residual_energy_cogen = max(electric_energy_cogen[i] - requested_energy, 0)
        requested_energy -= min(electric_energy_cogen[i], requested_energy)

        # from PV
        PV_hourly_production = pd.read_csv("././resources/PV_data.csv", header=None)
        PV_hourly_production = PV_hourly_production[2]
        residual_energy_pv = max(
            PV_hourly_production[i] - requested_energy, 0
        )  # Energia PV non consumata dall'utente
        requested_energy -= min(PV_hourly_production[i], requested_energy)

        # Charge the battery with excess energy (from PV or cogenerator)
        aviable_battery_energy += residual_energy_pv + residual_energy_pv
        aviable_battery_energy = min(
            aviable_battery_energy, battery_size
        )  # Limit capacity to battery size

        # If there is still demand, try to satisfy it with the battery
        if requested_energy > 0:
            requested_energy_from_battery = min(
                aviable_battery_energy, requested_energy
            )
            requested_energy -= requested_energy_from_battery
            aviable_battery_energy -= requested_energy_from_battery

        # If there is still demand, it draws energy from the grid
        if requested_energy > 0:
            energy_from_grid += requested_energy

        energy_covered += initial_requested_energy - requested_energy

    # COSTS
    years = 20
    # Electricity form grid
    cost_electricity_from_grid = energy_from_grid * common.ELECTRIC_ENERGY_PRICE
    # Installation of PV
    cost_installation_PV = cost_PV_installation(PV_size)
    # Installation of battery
    cost_installation_battery = battery_size * common.COST_INSTALLATION_BATTERY
    # total costs over time period
    total_cost = (
        cost_installation_PV
        + cost_installation_battery
        + cost_electricity_from_grid * years
    )

    # Electricity consumption coverage percentage
    percentage_electric_coverage = energy_covered / np.sum(electric_consumption)

    # Final function: alpha controls the relative importance of minimizing costs vs maximizing coverage
    alpha = 0.8
    objective_function = (1 - alpha) * total_cost - alpha * percentage_electric_coverage
    return objective_function


def optimizer(electric_consumption, thermal_consumption):
    initial_guess = [10, 0]
    result = minimize(
        cost_function,
        initial_guess,
        args=(electric_consumption, thermal_consumption),
        bounds=[(0, 1000), (0, 10)],
    )
    PV_size, battery_size = result.x
    return PV_size, battery_size


def test_optimizer():
    test_data = pd.read_csv(
        "././resources/Dati_Simulati_di_Consumi_Elettrici_e_Termici.csv"
    )
    thermal_consumption = test_data["Consumo_Termico_kWh"]
    electric_consumption = test_data["Consumo_Elettrico_kWh"]
    PV_size, battery_size = optimizer(electric_consumption, thermal_consumption)
    print(PV_size, battery_size)
    __import__("ipdb").set_trace()


test_optimizer()
