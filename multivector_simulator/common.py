import pandas as pd
import numpy as np
from typing import Annotated

from pydantic import AfterValidator, Field


def validate_consumption_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Verifica che le colonne inserite siano compatibili con quelle richieste
    required_columns = [
        "Ora",
        "Consumi elettrici (kWh)",
        "Consumi Termici (J)",
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


ConsumptionDataFrameType = Annotated[
    pd.DataFrame,
    AfterValidator(validate_consumption_dataframe),
    Field(description="Dataframe not compatible"),
]


ELECTRIC_EFFICIENCY_COGEN = 0.35
THERMAL_EFFICIENCY_COGEN = 0.45
COST_INSTALLATION_COGEN = 1200  # cost of installation of cogenerator for kW
COST_GAS_FOR_GEN = 0.4  # cost of gas for cogenerator in €/Smc
COST_INSTALLATION_BATTERY = 1000  # cost of installation of battery for kWh

ELECTRIC_ENERGY_PRICE = 0.16  # cost of electricity from the grid, €/kWh
THERMAL_ENERGY_PRICE = 0.055  # cost of thermal energy from the grid, €/kWh


def PV_year_production() -> pd.DataFrame:
    PV_data = pd.read_csv("././resources/PV_data.csv", header=None)
    PV_year_production = PV_data[2]
    return PV_year_production
