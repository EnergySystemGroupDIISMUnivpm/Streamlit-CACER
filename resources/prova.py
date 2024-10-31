import pandas as pd
import numpy as np
from multivector_simulator import common

file_esempio = pd.read_excel(
    "resources/Prova_input_consumi_multienergetico.xlsx", engine="openpyxl"
)
consumi_elettrici = np.nansum(file_esempio["Consumi Elettrici (kWh)"])
consumi_termici = np.nansum(file_esempio["Consumi Termici (kWh)"])
consumi_frigo = np.nansum(file_esempio["Consumi Frigoriferi (kWh)"])

costo_annuale_energia = (
    consumi_elettrici * common.ELECTRIC_ENERGY_PRICE
    + consumi_termici * common.THERMAL_ENERGY_PRICE
)

print(costo_annuale_energia)
