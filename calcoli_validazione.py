import matplotlib.pyplot as plt
import numpy as np


def plot_daily_production(ax, data_production, data_consumption, date_label, day_index):
    start = day_index * 24
    end = start + 24  # Calculate the end index
    ax.plot(data_production[start:end])
    ax.plot(data_consumption[start:end])
    ax.set_xlabel("Ora")
    ax.set_ylabel("kWh")
    ax.set_title(date_label)


def calculate_median_over_period(data: np.ndarray, hours: int) -> np.ndarray:
    """
    Calculate the median profile of production or consumption over a period.
    Args:
        data: array - production or consumption data
        hours: int - number of hours in the period (e.g., 24 for a daily profile)
    Returns:
        median_profile: np.ndarray - median values for each hour within the period
    """
    # Reshape data to split into days, each with the specified number of hours
    reshaped_data = data[: len(data) // hours * hours].reshape(-1, hours)

    # Calculate the median across each hour (column-wise median)
    median_profile = np.median(reshaped_data, axis=0)

    return median_profile


def plot_monthly_median_profile(
    ax, data_production, data_consumption, month_label, start_day
):
    # Calculate the start and end indices for the month
    start = start_day * 24
    end = start + (30 * 24)  # Approximate each month as 30 days

    # Calculate median profiles for production and consumption
    median_production_profile = calculate_median_over_period(
        data_production[start:end], 24
    )
    median_consumption_profile = calculate_median_over_period(
        data_consumption[start:end], 24
    )

    # Plot the median profiles
    ax.plot(median_production_profile, label="Produzione Mediana")
    ax.plot(median_consumption_profile, label="Consumo Mediano")
    ax.set_xlabel("Ora del Giorno")
    ax.set_ylabel("kWh")
    ax.set_title(month_label)
    ax.legend()


# PLOT 1 DAY OF MONTH
def day_monthly_plots(
    electric_production_pv, electric_production_cogen, electric_consumption
):  # Create a figure with 12 subplots arranged in a grid
    fig, axs = plt.subplots(3, 4, figsize=(15, 10))  # 3 rows, 4 columns for 12 months

    # Define starting days for the first day of each month
    start_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    month_labels = [
        "1 Gennaio",
        "1 Febbraio",
        "1 Marzo",
        "1 Aprile",
        "Maggio",
        "1 Giugno",
        "1 Luglio",
        "1 Agosto",
        "1 Settembre",
        "1 Ottobre",
        "1 Novembre",
        "1 Dicembre",
    ]

    # Loop over each month and plot on the corresponding subplot
    for i, (ax, day, label) in enumerate(zip(axs.flatten(), start_days, month_labels)):
        plot_daily_production(
            ax, electric_production_pv, electric_consumption, label, day
        )

    plt.tight_layout()  # Adjust layout for better spacing
    plt.savefig("first_day_monthly_plots.png")  # Save the figure with all subplots


# PLOT MEDIAN OF EACH MONTH
def monthly_median(
    electric_production_pv, electric_production_cogen, electric_consumption
):

    # Create a figure with 12 subplots arranged in a grid
    fig, axs = plt.subplots(3, 4, figsize=(15, 10))  # 3 rows, 4 columns for 12 months
    # Define starting days for the first day of each month
    start_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    month_labels = [
        "Gennaio",
        "Febbraio",
        "Marzo",
        "Aprile",
        "Maggio",
        "Giugno",
        "Luglio",
        "Agosto",
        "Settembre",
        "Ottobre",
        "Novembre",
        "Dicembre",
    ]

    # Loop over each month and plot on the corresponding subplot
    for ax, day, label in zip(axs.flatten(), start_days, month_labels):
        plot_monthly_median_profile(
            ax, electric_production_pv, electric_consumption, label, day
        )

    plt.tight_layout()  # Adjust layout for better spacing
    plt.savefig("monthly_median_profiles.png")  # Save the figure with all subplots


def calculations(
    electric_production_pv, electric_production_cogen, electric_consumption
):
    central_hours = range(10, 16)

    # Count occurrences where production > consumption for the specified hours each day
    electric_prod = electric_production_pv + electric_production_cogen
    count = sum(
        1
        for day in range(365)  # 365 days in a year
        for hour in central_hours
        if electric_prod[day * 24 + hour] > electric_consumption[day * 24 + hour]
    )
    print(
        f"""numero di volte in cui la produzione > consumo nelle ore centrali della giornata: {count}"""
    )

    count2 = sum(
        1
        for pv, consumption in zip(
            electric_production_pv + electric_production_cogen,
            electric_consumption,
        )
        if pv > consumption
    )
    print(f"""numero di volte in cui la produzione > consumo : {count2}""")


def validazione(
    electric_production_pv, electric_production_cogen, electric_consumption
):
    day_monthly_plots(
        electric_production_pv, electric_production_cogen, electric_consumption
    )
    monthly_median(
        electric_production_pv, electric_production_cogen, electric_consumption
    )
    calculations(
        electric_production_pv, electric_production_cogen, electric_consumption
    )
