import pandas as pd
import numpy as np

# Carica il file Excel
file_esempio = pd.read_excel("Prova_input_consumi_PV_cogen.xlsx")

# Fill in the 'Consumi Frigoriferi (kWh)' with 20% of total consumption where it's None
file_esempio["Consumi Totali (kWh)"] = (
    file_esempio["Consumi Elettrici (kWh)"]
    + file_esempio["Consumi Termici (kWh)"].fillna(0)
    + file_esempio["Consumi Frigoriferi (kWh)"].fillna(0)
)

# Calculate the required frigoriferi and termici
required_frigoriferi = file_esempio["Consumi Totali (kWh)"] * 0.2
required_termici = file_esempio["Consumi Totali (kWh)"] * 0.4

# Apply the new values
file_esempio["Consumi Frigoriferi (kWh)"] = file_esempio.apply(
    lambda row: max(
        (
            row["Consumi Frigoriferi (kWh)"]
            if pd.notna(row["Consumi Frigoriferi (kWh)"])
            else 0
        ),
        row["Consumi Totali (kWh)"] * 0.2,
    ),
    axis=1,
)

file_esempio["Consumi Termici (kWh)"] = file_esempio.apply(
    lambda row: max(row["Consumi Termici (kWh)"], row["Consumi Totali (kWh)"] * 0.4),
    axis=1,
)


# Remove 'Consumi Totali' as it was just for calculation purposes
file_esempio = file_esempio.drop(columns=["Consumi Totali (kWh)"])
file_esempio["Consumi Elettrici (kWh)"] = file_esempio["Consumi Elettrici (kWh)"] / 2

file_esempio.to_excel("Esempio_input_consumi_PV_cogen.xlsx", index=False)
