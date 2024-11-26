from pydantic import PositiveFloat
from multivector_simulator.models import model
import numpy as np


def sizes_energies_costs(
    electric_consumption,
    thermal_consumption,
    refrigeration_consumption,
    LabelCogTrigen,
    start_winter_season,
    end_winter_season,
):
    """
    Calculation of the best sizes of PV, battery and cogen/trigen and relative savings, investment costs, total costs, percentage of energy coverage.
    Attrs:
    electric_consumption: np.ndarray - electric annual consumptions in kWh
    thermal_consumption: np.ndarray - thermal annual consumptions in kWh
    refrigerator_consumption: np.ndarray - refrigerator annual consumption in kWh
    LabelCogTrigen: str - indicating "Cogen" or "Trigen"
    start_winter_season: NonNegativeInt - start month of the winter season (0=January)
    end_winter_season: NonNegativeInt - end month of the winter season (0=January)

    Returns:
    Tuple cotaining:
    -PV_size: NonNegativeInt - best pv size in KW
    -cogen_size: NonNegativeInt - best cogen size in kW if label is Cogen else is 0
    -trigen_size: NonNegativeInt - best trigen size in kW if label is Trigen else is 0
    -battery_size: NonNegativeInt - best battery size in kW
    -savings: PositiveFloat - annual savings in euro from the usage of the best sizes over a period of one year considering the energy that is not purchased from the gird
    -investment_costs: PositiveFloat - total costs in euro of installation of battery, pv, cogen/trigen
    -total_costs: PositiveFloat - annual total costs in euro of installations, maintenance and usage of gas from cogen/trigen and pv/battery
    -cost_gas: PositiveFloat - annual cost of gas in euro from cogen/trigen for 1 year
    """
    # OPTIMAL SIZES
    (PV_size, battery_size, cogen_trigen_size) = model.optimizer(
        electric_consumption,
        thermal_consumption,
        refrigeration_consumption,
        LabelCogTrigen,
        start_winter_season,
        end_winter_season,
    )

    if LabelCogTrigen == "Cogen":
        trigen_size = 0
        cogen_size = cogen_trigen_size
    else:
        cogen_size = 0
        trigen_size = cogen_trigen_size

    # ENERGY COVERAGE
    # from cogen/trigen
    (
        electric_energy_from_grid,
        thermal_energy_from_grid,
        refrigeration_energy_from_grid,
        self_consumption_electric_energy_from_cogen_trigen,
        self_consumption_thermal_energy_from_cogen_trigen,
        self_consumption_refrigeration_energy_from_cogen_trigen,
        available_battery_energy_from_cogen_trigen,
    ) = model.calculate_cogen_or_trigen_energy_coverage(
        thermal_consumption,
        refrigeration_consumption,
        electric_consumption,
        cogen_trigen_size,
        LabelCogTrigen,
        start_winter_season,
        end_winter_season,
    )
    # from pv/battery
    (
        energy_from_grid_pv_battery,
        self_consumed_energy_battery_pv,
        self_consumed_energy_battery_cogen,
        self_consumption_electric_energy_from_pv,
    ) = model.determination_electric_coverage_year_PV_battery(
        electric_consumption - self_consumption_electric_energy_from_cogen_trigen,
        available_battery_energy_from_cogen_trigen,
        PV_size,
        battery_size,
    )

    # calculation of the total energies in a year
    energy_store_battery_from_cogen_trigen = np.nansum(
        self_consumed_energy_battery_cogen
    )
    total_self_consump_electric_cogen_trigen = np.nansum(
        self_consumption_electric_energy_from_cogen_trigen
    )
    total_self_consumption_electric_energy_from_pv = np.nansum(
        self_consumption_electric_energy_from_pv
    )
    total_self_consumed_energy_from_battery = np.nansum(
        self_consumed_energy_battery_pv
    ) + np.nansum(self_consumed_energy_battery_cogen)
    total_self_consumed_energy_electric = (
        total_self_consumed_energy_from_battery
        + total_self_consump_electric_cogen_trigen
        + total_self_consumption_electric_energy_from_pv
    )
    total_self_consumed_energy_thermal = np.nansum(
        self_consumption_thermal_energy_from_cogen_trigen
    )
    total_self_consumed_energy_refrigeration = np.nansum(
        self_consumption_refrigeration_energy_from_cogen_trigen
    )

    # INVESTIMENTS
    quantity_used_gas_cogen_trigen = model.cogen_trigen_usage_gas(
        cogen_trigen_size, 24 * 365
    )
    investment_costs = model.total_cost_investment(
        PV_size, battery_size, cogen_trigen_size, LabelCogTrigen
    )
    cost_gas = model.cost_gas_used_cogen_trigen(quantity_used_gas_cogen_trigen)
    savings = model.savings_using_implants(
        total_self_consumed_energy_electric,
        total_self_consumed_energy_thermal,
        total_self_consumed_energy_refrigeration,
    )

    annual_maintenance_cost = model.maintenance_cost_cogen_trigen(
        cogen_trigen_size, LabelCogTrigen
    ) + model.maintenance_cost_PV(PV_size, battery_size)

    total_costs = investment_costs + cost_gas + annual_maintenance_cost

    return (
        PV_size,
        cogen_size,
        trigen_size,
        battery_size,
        savings,
        investment_costs,
        total_costs,
        cost_gas,
    )
