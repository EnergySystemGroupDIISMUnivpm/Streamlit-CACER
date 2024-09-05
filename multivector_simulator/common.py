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
    if df.shape[0] != 8775:
        raise ValueError(
            "Il numero di righe inserite non è corretto. Devono essere presenti 8776 righe, una per ogni ora dell'anno."
        )
    return df


ConsumptionDataFrameType = Annotated[
    pd.DataFrame,
    AfterValidator(validate_consumption_dataframe),
    Field(description="Dataframe not compatible"),
]
