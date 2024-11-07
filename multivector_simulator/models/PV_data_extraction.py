import pandas as pd

PV_data = pd.read_csv("././resources/PV_data.csv", header=None)
PV_year_production = PV_data[2]
PV_year_production.to_csv("././resources/PV_year_production.csv", index=False)
