import pandas as pd
import numpy as np
from typing import Annotated

from pydantic import AfterValidator, Field, BaseModel, PositiveInt

from cacer_simulator.common import PositiveOrZeroFloat


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


ELECTRIC_EFFICIENCY_COGEN = 0.35
THERMAL_EFFICIENCY_COGEN = 0.45
COST_INSTALLATION_COGEN = 1200  # cost of installation of cogenerator for kW
COST_GAS_FOR_GEN = 0.4  # cost of gas for cogenerator in €/Smc
CONSUMPTION_COGEN_HOUR = 0.105  # Consumption by 1kW cogenerator of gas in Smc for each hour, working at full capacity
COST_INSTALLATION_BATTERY = 1000  # cost of installation of battery for kWh
COGEN_CONVERSION_FACTOR = (9.52 / ELECTRIC_EFFICIENCY_COGEN) + (
    9.52 / THERMAL_EFFICIENCY_COGEN
)  # factor that allows to pass from Smc used by cogenerator to the quantity of energy producted

ELECTRIC_ENERGY_PRICE = 0.16  # cost of electricity from the grid, €/kWh
THERMAL_ENERGY_PRICE = 0.055  # cost of thermal energy from the grid, €/kWh


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

AVG_EMISSIONS_FACTOR_ELETRICITY = 0.309  # how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
AVG_EMISSIONS_FACTOR_THERMAL = 0.2  # how much CO2 is emitted for each kWh produced by the italian traditional thermal grid (kg CO2/kWh)


class Optimizer(BaseModel):
    ALPHA: PositiveOrZeroFloat = (
        0.5  # balance between minimizing costs and maximizing coverage
    )
    INITIAL_GUESS: list[int] = [0, 10]  # initial guess for PV and Battery sizes
    BOUNDS: list[tuple[int, int]] = [
        (0, 1000),
        (0, 50),
    ]  # bounds for PV and Battery sizes
    YEARS: PositiveInt = 20  # years to be considered for the calculation of cost
    COGEN_COVERAGE: PositiveOrZeroFloat = (
        0.7  # trashold, how many hours has the cogenerator to cover. see:https://industriale.viessmann.it/blog/dimensionare-cogeneratore-massima-efficienza
    )
