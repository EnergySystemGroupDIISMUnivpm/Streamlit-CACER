import pandas as pd
import matplotlib.pyplot as plt

dataset_charging_consump = pd.read_csv(
    "resources/ConsumiColonnineCalifornia.csv", sep=","
)
dataset_charging_consump["Start Date"] = pd.to_datetime(
    dataset_charging_consump["Start Date"], errors="coerce"
)
dataset_charging_consump["anno"] = dataset_charging_consump["Start Date"].dt.year
dataset_charging_consump["Total Duration (hh:mm:ss)"] = pd.to_timedelta(
    dataset_charging_consump["Total Duration (hh:mm:ss)"]
)

total_duration_per_station_year = (
    dataset_charging_consump.groupby(["Station Name", "anno"])[
        "Total Duration (hh:mm:ss)"
    ]
    .sum()
    .reset_index()
)
total_duration_per_station_year["Total Duration (seconds)"] = (
    total_duration_per_station_year["Total Duration (hh:mm:ss)"].dt.total_seconds()
)

average_duration_per_year = (
    total_duration_per_station_year.groupby("anno")["Total Duration (seconds)"]
    .mean()
    .reset_index()
)

average_duration_per_year["Average Duration (hours)"] = (
    average_duration_per_year["Total Duration (seconds)"] / 3600
)

average_duration_per_year.drop(["Total Duration (seconds)"], axis=1)
plt.bar(
    average_duration_per_year["anno"],
    average_duration_per_year["Average Duration (hours)"],
)
plt.show()
