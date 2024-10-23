from tkinter import N
from matplotlib import tri
import pandas as pd
import numpy as np
from typing import ClassVar, List, Tuple, Optional, Annotated

from pydantic import (
    AfterValidator,
    Field,
    BaseModel,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
)

from cacer_simulator.common import PositiveOrZeroFloat

AVG_EMISSIONS_FACTOR_ELETRICITY = 0.309  # how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
AVG_EMISSIONS_FACTOR_THERMAL = 0.2  # how much CO2 is emitted for each kWh produced by the italian traditional thermal grid (kg CO2/kWh)

HOURS_OF_YEAR = 8760


# cogenerator/trigenerator
class Trigen_Cogen(BaseModel):
    COST_GAS_FOR_GEN: PositiveFloat = (
        0.4  # cost of gas for cogenerator/trigenerator in €/Smc
    )
    CONSUMPTION_COGEN_HOUR: PositiveFloat = (
        0.105  # Consumption by 1kW cogenerator/trigenerator of gas in Smc for each hour, working at full capacity
    )
    COGEN_CONVERSION_FACTOR: PositiveFloat = (
        9.52  # PCI: allows to pass from Smc of burned gas to quantity of energy produced (kWh).
    )
    MINIMAL_THERMAL: PositiveFloat = (
        0.4  # the thermal consumption must be at least 40% of the total consumpitons to have a cogen or trigen
    )
    MINIMAL_REFRIGERATOR: PositiveFloat = (
        0.2  # the refrigerator consumption must be at least 20% of the total consumpitons to have a trigenerator
    )

    class Cogenerator(BaseModel):
        ELECTRIC_EFFICIENCY_COGEN: PositiveFloat = (
            0.3  # eletric efficiency of cogenerator. For 1kWh of energy of gas, 0.3kWh of eletricity are produced.
        )
        THERMAL_EFFICIENCY_COGEN: PositiveFloat = (
            0.5  # thermal efficiency of cogenerator. For 1kWh of energy of gas, 0.5kWh of thermal energy are produced.
        )

        # cost of 1kW of cogenerator in euro
        kw_cost_cogen: dict[tuple[float, float], int] = {
            (0, 1000): 1200,
            (1000, float("inf")): 800,
        }

        def get_kw_cost_cogen(
            self, cogenerator_size: NonNegativeInt | PositiveOrZeroFloat
        ) -> int:

            if cogenerator_size <= 0:
                return 0
            else:
                for power_range, cost in self.kw_cost_cogen.items():
                    if power_range[0] <= cogenerator_size < power_range[1]:
                        return cost
            return 0

    class Trigenerator(BaseModel):
        ELECTRIC_EFFICIENCY_TRIGEN: PositiveFloat = (
            0.3  # eletric efficiency of trigenerator. For 1kWh of energy of gas, 0.3kWh of eletricity are produced.
        )
        THERMAL_EFFICIENCY_TRIGEN: PositiveFloat = (
            0.3  # thermal efficiency of trigenerator. For 1kWh of energy of gas, 0.3kWh of thermal energy are produced.
        )
        REFRIGERATION_EFFICIENCY_TRIGEN: PositiveFloat = (
            0.2  # refrigeration efficiency of trigenerator. For 1kWh of energy of gas, 0.2kWh of refrigeneration are produced.
        )

        kw_cost_trigen: dict[tuple[float, float], int] = {
            (0, 1000): 2000,
            (1000, float("inf")): 1200,
        }

        def get_kw_cost_trigen(
            self, trigenerator_size: NonNegativeInt | PositiveOrZeroFloat
        ) -> int:

            if trigenerator_size <= 0:
                return 0
            else:
                for power_range, cost in self.kw_cost_trigen.items():
                    if power_range[0] <= trigenerator_size < power_range[1]:
                        return cost
            return 0


COST_INSTALLATION_BATTERY = 1000  # cost of installation of battery for kWh


ELECTRIC_ENERGY_PRICE = 0.16  # cost of electricity from the grid, €/kWh
THERMAL_ENERGY_PRICE = 0.055  # cost of thermal energy from the grid, €/kWh


def validate_consumption_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Verifica che le colonne inserite siano compatibili con quelle richieste
    required_columns = [
        "Ora",
        "Consumi Elettrici (kWh)",
        "Consumi Termici (kWh)",
        "Consumi Frigoriferi (kWh)",
    ]
    for col in df.columns:
        if col not in required_columns:
            raise ValueError(f"La colonna '{col}' non può essere inserita nell'Excel.")

    # Verifica che le colonne richieste siano presenti
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"La colonna '{col}' deve essere presente nell'Excel.")

    # Verifica che tutti i valori nelle colonne siano NaN o >= 0
    for col in required_columns:
        invalid_values = df[(~df[col].isna()) & (df[col] < 0)]
        if not invalid_values.empty:
            raise ValueError(
                f"La colonna '{col}' contiene valori negativi nelle righe: {invalid_values.index.tolist()}"
            )
    # Verifica che il numero di righe sia corretto
    if df.shape[0] != 8760:
        raise ValueError(
            "Il numero di righe inserite non è corretto. Devono essere presenti 8760 righe, una per ogni ora dell'anno."
        )
    return df


pv_production_hourly = pd.read_csv("././resources/PV_data.csv", header=None)[
    2
].to_numpy()


ConsumptionDataFrameType = Annotated[
    pd.DataFrame,
    AfterValidator(validate_consumption_dataframe),
    Field(description="Dataframe not compatible"),
]


def PV_year_production() -> pd.Series:
    PV_data = pd.read_csv("././resources/PV_data.csv", header=None)
    PV_annual_production = PV_data[2]
    return PV_annual_production


PERIOD_TO_BE_PLOTTED = {"giornaliera": 24, "settimanale": 168, "mensile": 720}
period_labels_list = list(PERIOD_TO_BE_PLOTTED.keys())


def is_valid_period_labels_list(x: str) -> str:
    if x not in period_labels_list:
        raise ValueError(
            f"Invalid Lable for period {x}, must be in {period_labels_list}"
        )
    return x


LabelPeriodLabelsList = Annotated[
    str,
    AfterValidator(is_valid_period_labels_list),
    Field(description=f"Label use case among {period_labels_list}"),
]

ENERGY_TYPE = ["Elettrica", "Termica", "Frigorifera"]


def is_valid_energy_type(x: str) -> str:
    if x not in period_labels_list:
        raise ValueError(f"Invalid Lable for energy {x}, must be in {ENERGY_TYPE}")
    return x


LabelEnergyType = Annotated[
    str,
    AfterValidator(is_valid_energy_type),
    Field(description=f"Label use case among {ENERGY_TYPE}"),
]


class Optimizer(BaseModel):
    ALPHA: PositiveOrZeroFloat = (
        0.5  # balance between minimizing costs and maximizing coverage
    )
    INITIAL_GUESS: list[NonNegativeInt] = [
        100,
        0,
        10,
    ]  # initial guess for PV and Battery sizes
    BOUNDS: ClassVar[List[Tuple[Optional[int], Optional[int]]]] = [
        (0, None),  # Bound per PV size
        (0, None),  # Bound per Battery size
        (0, None),  # Bound per cogen/trigen size
    ]
    YEARS: PositiveInt = 20  # years to be considered for the calculation of cost
