import numpy as np
from pydantic import NonNegativeInt, PositiveFloat, validate_call, PositiveInt
import multivector_simulator.common as common
from typing import Tuple
from cacer_simulator.common import PositiveOrZeroFloat, get_kw_cost
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt


def energy_self_consumed(
    produced_energy: np.ndarray, consumed_energy: np.ndarray
) -> np.ndarray:
    self_consumption = np.minimum(produced_energy, consumed_energy)
    return self_consumption


def cost_battery_installation(battery_size: PositiveInt) -> PositiveFloat:
    cost_battery = battery_size * common.COST_INSTALLATION_BATTERY
    return cost_battery


def cost_cogen_installation(cogen_size: PositiveInt) -> PositiveFloat:
    cost_cogen = cogen_size * common.COST_INSTALLATION_COGEN
    return cost_cogen


def cogen_usage_gas(
    cogen_size: PositiveInt, working_hours: PositiveInt
) -> PositiveFloat:
    """
    Calculation of the quantity (Smc) of gas used by cogenerator to work for a certain amount of hours working at full capacity.
    """
    used_gas = cogen_size * working_hours * common.CONSUMPTION_COGEN_HOUR
    return used_gas


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


def savings_using_implants(
    energy_from_pv: PositiveOrZeroFloat,
    energy_from_battery: PositiveOrZeroFloat,
    energy_from_cogen: PositiveOrZeroFloat,
) -> PositiveOrZeroFloat:
    """
    Calculation of the savings in euro using PV, battery end/or cogenerator.
    Attrs:
        energy_from_pv: PositiveOrZeroFloat - used electric energy from PV in kWh
        energy_from_battery: PositiveOrZeroFloat - used electric energy from battery in kWh
        energy_from_cogen: PositiveOrZeroFloat - used thermal energy from cogenerator in kWh
    """
    savings = (
        (energy_from_pv + energy_from_battery) * common.ELECTRIC_ENERGY_PRICE
        + energy_from_cogen * common.THERMAL_ENERGY_PRICE
    )
    return savings


def calc_payback_time(
    savings: PositiveOrZeroFloat, investment: PositiveOrZeroFloat
) -> NonNegativeInt:
    """
    Calculation of the payback time in years.
    Attrs:
        savings: PositiveOrZeroFloat - savings in euro of each year, obtained by the usage of PV, battery and/or cogenerator.
        investment: PositiveOrZeroFloat - investment in euro
    """
    payback_time = savings / investment
    payback_time = round(payback_time)
    return payback_time


def savings_in_a_period(savings: PositiveFloat, period: PositiveInt) -> PositiveFloat:
    """Calculation of the savings over a period of time.
    Attrs:
        savings: PositiveFloat - savings in euro
        period: PositiveInt - period in years"""
    savings_period = savings * period
    return savings_period


def calculate_cogen_size_optimized(
    thermal_consumption: np.ndarray, thermal_efficiency=common.THERMAL_EFFICIENCY_COGEN
) -> int:
    """
    Calculation of the best size in kW of cogenerator based on the thermal consumption.
    """
    threshold = common.Optimizer().COGEN_COVERAGE
    # Sort the heat consumption in decreasing order
    sorted_consumption = np.sort(thermal_consumption)[::-1]

    # Power required to cover the threshold of the time
    threshold_hours = int(threshold * len(thermal_consumption))
    size_cogen = sorted_consumption[threshold_hours] / thermal_efficiency
    print(f"""Optimal cogenerator size: {size_cogen} kW""")
    return round(size_cogen)


def production_cogen_optimized(size_cogen: int) -> Tuple[float, float]:
    """
    Calculate the electric and thermal unitary production based on the size of the cogenerator. Production in one hour.
    Attrs:
        size_cogen: int - size of the cogenerator in kW
    """
    electric_production = size_cogen * common.ELECTRIC_EFFICIENCY_COGEN
    thermal_production = size_cogen * common.THERMAL_EFFICIENCY_COGEN
    return electric_production, thermal_production


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
        np.sum(annual_energy_from_grid) * common.ELECTRIC_ENERGY_PRICE
    )
    cost_installation_PV = cost_PV_installation(PV_size)
    cost_installation_battery = cost_battery_installation(battery_size)
    total_cost = (
        cost_installation_PV
        + cost_installation_battery
        + (cost_electricity_from_grid * years)
    )
    return total_cost
def calculation_pv_production(pv_size):
    pv_production = common.pv_production_hourly * pv_size
    return pv_production

def determination_electric_coverage_year(
    electric_consumption,
    aviable_battery_energy: np.ndarray,
    pv_size: PositiveInt,
    battery_size: PositiveInt,
):
    """
    Determination of the eletric coverage per year covedered by PV and battery; and energy taken from the grid (kWh).

    Attrs:
        electric_consumption: float - electric yearly consumption in kWh
        aviable_battery_energy: array - energy available at the beginning to be stored in battery in kWh
        pv_size: PositiveInt - size of the PV plant in kW
        pv_unitary_production: array - PV hourly production in kWh, for a PV of 1 kW
        battery_size: PositiveInt - size of the battery in kWh
    """
    # Precompute PV production scaled by size
    
    pv_production = calculation_pv_production(pv_size)

    # Initialize arrays for tracking energy
    energy_from_grid = np.zeros_like(electric_consumption)
    energy_covered = np.zeros_like(electric_consumption)
    initial_energy_consumption = electric_consumption
    aviable_battery_energy = np.clip(aviable_battery_energy, 0, battery_size)

    # Energy from PV
    excess_energy_pv = np.where(
        pv_production - electric_consumption > 0,
        pv_production - electric_consumption,
        0,
    )
    electric_consumption = np.clip(electric_consumption - pv_production, 0, None)
    aviable_battery_energy = np.clip(
        aviable_battery_energy + excess_energy_pv, 0, battery_size
    )

    # energy from battery
    electric_consumption = np.clip(
        electric_consumption - aviable_battery_energy, 0, None
    )

    # energy from grid
    energy_from_grid = electric_consumption

    # Coverage of consumption
    energy_covered = initial_energy_consumption - energy_from_grid
    return energy_covered, energy_from_grid


def calculation_energy_cogen(
    electric_consumption, thermal_consumption
) -> tuple[np.ndarray, np.ndarray]:
    """
    Annual production of electric energy from cogenerator.
    """
    threshold = common.Optimizer().COGEN_COVERAGE
    size_cogen = calculate_cogen_size_optimized(
        thermal_consumption,
        thermal_efficiency=common.THERMAL_EFFICIENCY_COGEN,
    )
    electric_energy_cogen_hourly, thermal_energy_cogen_hourly = (
        production_cogen_optimized(size_cogen)
    )

    # Precompute the cogenerator production across the entire year
    electric_energy_cogen = np.full_like(
        electric_consumption, electric_energy_cogen_hourly
    )


    # Precompute the cogenerator production across the entire year
    thermal_energy_cogen = np.full_like(
        thermal_consumption, thermal_energy_cogen_hourly
    )
    plt.plot(
        range(len(electric_energy_cogen)),
        electric_energy_cogen,
        label="E Production Cogen",
        color="blue",
    )
    return electric_energy_cogen, thermal_energy_cogen


def energy_used_from_cogen(
    electric_energy_cogen, electric_consumption
) -> tuple[np.ndarray, np.ndarray]:
    """
    Quantity of energy used from the cogenerator and quantity of still available energy producted by the cogenerator (kWh).
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


def cost_function(
    x, electric_consumption, available_energy_battery
):
    """
    Determination of the objective function to be minimized.
    """

    PV_size, battery_size = x

    energy_covered, energy_from_grid = determination_electric_coverage_year(
        electric_consumption,
        available_energy_battery,
        PV_size,
        battery_size,
    )

    # Percentage of electric consumption coverage
    percentage_electric_coverage = np.sum(energy_covered) / np.sum(electric_consumption)

    # COSTS
    total_cost = total_economic_cost_PV_battery_grid(
        energy_from_grid, PV_size, battery_size
    )

    # Final objective function: balance between minimizing costs and maximizing coverage
    alpha = 0.6
    objective_function = (1 - alpha) * total_cost - alpha * percentage_electric_coverage
    return objective_function




def optimizer(electric_consumption, thermal_consumption):
    electric_energy_production_cogen = calculation_energy_cogen(
        electric_consumption, thermal_consumption
    )
    electric_consumption, available_energy_battery = energy_used_from_cogen(
        electric_energy_production_cogen, electric_consumption
    )
    # available_energy_battery = np.zeros_like(electric_consumption)
    initial_guess = (
        common.Optimizer().INITIAL_GUESS
    )  # Guess for PV size and battery size
    result = minimize(
        cost_function,
        initial_guess,
        args=(
            electric_consumption,
            available_energy_battery,
        ),
        bounds=common.Optimizer().BOUNDS,  # Bounds for PV size and battery size
    )
    PV_size, battery_size = result.x
    return round(PV_size), round(battery_size)


def test_optimizer():
    thermal_consumption = (
        pd.read_excel("././resources/univpm_carichitermici.xlsx")[
            "Carico_Termico_MW"
        ].to_numpy()
        * 1000
    )
    electric_consumption = pd.read_csv(
        "././resources/Dati_consumi_elettrici_esempio.csv", header=None
    )
    electric_consumption = electric_consumption[1] * 1000
    plt.plot(
        range(len(electric_consumption)),
        electric_consumption,
        label="Consumption",
        color="red",
    )
    
    PV_size, battery_size = optimizer(electric_consumption, thermal_consumption)
    optimal_pv_production = common.pv_production_hourly * PV_size
    plt.plot(
        range(len(optimal_pv_production)),
        optimal_pv_production,
        label="PV production",
        color="green",
    )

    print(f"Optimal PV size: {PV_size}, Optimal battery size: {battery_size}")

def calculate_mean_over_period(data:np.ndarray, hours:int) -> np.ndarray:
    """
    Calculate the mean value of production or consumption of a period of time.
    Attrs:
        data: array - production or consumption data
        hours: int - number of hours in the period"""
    
    data_start=data[0:hours]
    for i in range(1, round((len(data)/hours))-1):
        data_start=data_start+data [hours*i+1:hours*(i+1)+1]
    mean_value=data_start/round(len(data)/hours)
    return mean_value



#test_optimizer()
# plt.legend()
# plt.show()
