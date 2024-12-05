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
    Calculation of the best sizes of PV, battery, cogen/trigen and heat pump relative savings, investment costs, total costs
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
    -heat_pump_size:  NonNegativeInt - best heat pump size in kW
    -savings: PositiveFloat - annual savings in euro from the usage of the best sizes over a period of one year considering the energy that is not purchased from the gird
    -investment_costs: PositiveFloat - total costs in euro of installation of battery, pv, cogen/trigen
    -total_costs: PositiveFloat - annual total costs in euro of installations, maintenance and usage of gas from cogen/trigen and pv/battery
    -cost_gas: PositiveFloat - annual cost of gas in euro from cogen/trigen for 1 year
    """
    # OPTIMAL SIZES
    (PV_size, battery_size, cogen_trigen_size, heat_pump_size) = (
        model.optimizer_multiple_runs(
            electric_consumption,
            thermal_consumption,
            refrigeration_consumption,
            LabelCogTrigen,
            start_winter_season,
            end_winter_season,
        )
    )
    if LabelCogTrigen == "Cogen":
        trigen_size = 0
        cogen_size = cogen_trigen_size
    else:
        cogen_size = 0
        trigen_size = cogen_trigen_size

    total_cost, annual_savings, used_gas = model.self_consum_costs_savings(
        electric_consumption,
        thermal_consumption,
        refrigeration_consumption,
        LabelCogTrigen,
        start_winter_season,
        end_winter_season,
        PV_size,
        battery_size,
        cogen_trigen_size,
        heat_pump_size,
    )
    investment_costs = model.total_cost_investment(
        PV_size, battery_size, cogen_trigen_size, LabelCogTrigen, heat_pump_size
    )
    cost_gas = model.cost_gas_used_cogen_trigen(used_gas)

    return (
        PV_size,
        cogen_size,
        trigen_size,
        battery_size,
        annual_savings,
        investment_costs,
        cost_gas,
    )
