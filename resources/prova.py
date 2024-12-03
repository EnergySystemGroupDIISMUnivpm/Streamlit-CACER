import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_esempio = pd.read_csv(
    "resources/PV_data.csv",
    delimiter=",",
    header=None,
)
pv_data = file_esempio[2]
# estate [3600:5760]
print(f"""media in estate {np.mean(pv_data[3600:5760])}""")
max_estate = max(pv_data[3600:5760])
print(f""" media Gennaio-Maggio {np.mean(pv_data[0:3600])}""")
print(f""" media Settembre-Dicembre {np.mean(pv_data[5760:])}""")
x1 = 3600
x2 = 5760
# Plot della funzione pv_data
plt.plot(pv_data, label="pv_data", color="blue")

# Linea verticale a x = 3600
plt.axvline(x=3600, color="red", linestyle="--", label="x = 3600")

# Linea verticale a x = 5760
plt.axvline(x=5760, color="green", linestyle="--", label="x = 5760")

plt.axhline(y=max_estate)  # type: ignore
plt.show()
