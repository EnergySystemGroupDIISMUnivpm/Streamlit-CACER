from multivector_simulator.models import model
import numpy as np


def sizes_energies_costs(
    electric_consumption, thermal_consumption, refrigeration_consumption, LabelCogTrigen
):

    # OPTIMAL SIZES
    (PV_size, battery_size, cogen_trigen_size) = model.optimizer(
        electric_consumption,
        thermal_consumption,
        refrigeration_consumption,
        LabelCogTrigen,
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
        cogen_size,
        LabelCogTrigen,
    )
    # from pv/battery
    (
        energy_covered_pv_battery,
        energy_from_pv_battery,
        self_consumed_energy_battery_pv,
        self_consumed_energy_battery_cogen,
        self_consumption_electric_energy_from_pv,
    ) = model.determination_electric_coverage_year_PV_battery(
        electric_consumption,
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
        [
            np.nansum(self_consumed_energy_battery_pv),
            np.nansum(self_consumed_energy_battery_cogen),
        ],
        axis=0,
    )
    total_self_consumed_energy_electric = np.nansum(
        [
            total_self_consumed_energy_from_battery,
            total_self_consump_electric_cogen_trigen,
            total_self_consumption_electric_energy_from_pv,
        ],
        axis=0,
    )
    total_self_consumed_energy_thermal = np.nansum(
        self_consumption_thermal_energy_from_cogen_trigen
    )
    total_self_consumed_energy_refrigeration = np.nansum(
        self_consumption_refrigeration_energy_from_cogen_trigen
    )

    # INVESTIMENTS
    quantity_used_gas_cogen_trigen = model.cogen_trigen_usage_gas(cogen_size, 24 * 365)
    investment_costs = model.total_cost_investment(
        PV_size, battery_size, cogen_size, LabelCogTrigen
    )
    cost_gas = model.cost_gas_used_cogen_trigen(quantity_used_gas_cogen_trigen)
    savings = (
        model.savings_using_implants(
            total_self_consumed_energy_electric,
            total_self_consumed_energy_thermal,
            total_self_consumed_energy_refrigeration,
        )
        - cost_gas
    )

    total_costs = investment_costs + cost_gas
    percentage_energy_coverage = (
        (total_self_consumed_energy_electric / np.nansum(electric_consumption))
        + (total_self_consumed_energy_thermal / np.nansum(thermal_consumption))
        + (
            total_self_consumed_energy_refrigeration
            / np.nansum(refrigeration_consumption)
        )
    )
    return (
        PV_size,
        cogen_size,
        trigen_size,
        battery_size,
        savings,
        investment_costs,
        total_costs,
        percentage_energy_coverage,
    )
