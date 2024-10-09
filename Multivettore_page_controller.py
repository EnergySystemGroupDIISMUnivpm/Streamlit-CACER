import streamlit as st
import pandas as pd
from multivector_simulator.views.view import UserInput, UserOuput, title_multivettore
from multivector_simulator.models import model
import numpy as np


def Simulator_Multivettore():
    title_multivettore()

    user_input = UserInput()
    consumption = user_input.download_upload_consumption()
    user_output = UserOuput()

    # Load consumption type
    if consumption is not None:
        eletric_consumption = consumption["Consumi Elettrici (kWh)"].to_numpy()
        thermal_consumption = consumption["Consumi Termici (kWh)"].to_numpy()
        refrigeration_consumption = consumption["Consumi Frigoriferi (kWh)"].to_numpy()
     
        # Insert button results
        if user_output.see_results():
            cogen_size = model.calculate_cogen_size_optimized(thermal_consumption)
            PV_size,  battery_size = model.optimizer(eletric_consumption, thermal_consumption)
             
            user_output.see_optimal_sizes(PV_size, cogen_size, battery_size)
            

            eletric_production_cogen, thermal_production_cogen = model.calculation_energy_cogen(eletric_consumption, thermal_consumption)
            eletric_production_pv = model.calculation_pv_production(PV_size)
            self_consumed_eletric = model.energy_self_consumed(eletric_production_cogen + eletric_production_pv, eletric_consumption)
            self_consumed_thermal = model.energy_self_consumed(thermal_production_cogen, thermal_consumption)
            user_output.see_coverage_energy_plot(eletric_consumption, eletric_production_cogen + eletric_production_pv, self_consumed_eletric, "Elettrica")
            user_output.see_coverage_energy_plot(thermal_consumption, thermal_production_cogen, self_consumed_thermal, "Termica")