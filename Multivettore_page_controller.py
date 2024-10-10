import streamlit as st
import pandas as pd
from multivector_simulator.views.view import UserInput, UserOuput, title_multivettore
from multivector_simulator.models import model
import numpy as np
import multivector_simulator.common as common


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
        if "see_results" not in st.session_state:
            st.session_state["see_results"] = False

        # Mostra il pulsante solo se non è stato premuto
        if not st.session_state["see_results"]:
            if user_output.see_results():
                st.session_state["see_results"] = True

        if st.session_state["see_results"]:

            cogen_size = model.calculate_cogen_size_optimized(thermal_consumption)
            PV_size,  battery_size = model.optimizer(eletric_consumption, thermal_consumption)
             
            user_output.see_optimal_sizes(PV_size, cogen_size, battery_size)
            

            eletric_production_cogen, thermal_production_cogen = model.calculation_energy_cogen(eletric_consumption, thermal_consumption)
            eletric_production_pv = model.calculation_pv_production(PV_size)
            self_consumed_eletric = model.energy_self_consumed(eletric_production_cogen + eletric_production_pv, eletric_consumption)
            self_consumed_thermal = model.energy_self_consumed(thermal_production_cogen, thermal_consumption)

            if "period_label" not in st.session_state:
                st.session_state["period_label"] = None
            st.session_state["period_label"]= user_input.select_period_plot()

            if st.session_state["period_label"] is not None:
                period_to_be_plot = user_output.extract_period_from_period_label(st.session_state["period_label"])
                electric_consumption_period = model.calculate_mean_over_period(eletric_consumption, period_to_be_plot)
                electric_production_period = model.calculate_mean_over_period(eletric_production_cogen + eletric_production_pv, period_to_be_plot)
                user_output.see_coverage_energy_plot(electric_consumption_period, electric_production_period, "Elettrica", st.session_state["period_label"])

                thermal_production_cogen_period = model.calculate_mean_over_period(thermal_production_cogen, period_to_be_plot)
                thermal_consumption_period = model.calculate_mean_over_period(thermal_consumption, period_to_be_plot)
                user_output.see_coverage_energy_plot(thermal_consumption_period, thermal_production_cogen_period, "Termica", st.session_state["period_label"])