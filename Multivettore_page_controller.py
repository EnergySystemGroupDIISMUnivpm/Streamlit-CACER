from math import e
import streamlit as st
import pandas as pd
from multivector_simulator.views.view import UserInput, UserOuput, title_multivettore
from multivector_simulator.models import model
import numpy as np
import multivector_simulator.common as common
import multivector_controller_wrapped_functions


def Simulator_Multivettore():
    title_multivettore()

    user_input = UserInput()
    consumption = user_input.download_upload_consumption()
    user_output = UserOuput()

    # Load consumption type
    if consumption is not None:
        electric_consumption = consumption["Consumi Elettrici (kWh)"].to_numpy()
        thermal_consumption = consumption["Consumi Termici (kWh)"].to_numpy()
        refrigeration_consumption = consumption["Consumi Frigoriferi (kWh)"].to_numpy()

        # Insert button results
        if "see_results" not in st.session_state:
            st.session_state["see_results"] = False

        if not st.session_state["see_results"]:
            if user_output.see_results():
                st.session_state["see_results"] = True

        if st.session_state["see_results"]:

            # calculation of the best size of cogen, pv, battery
            (
                PV_size_C,
                cogen_size_C,
                trigen_size_C,
                battery_size_C,
                savings_C,
                investment_costs_C,
                total_costs_C,
                percentage_energy_coverage_C,
            ) = multivector_controller_wrapped_functions.sizes_energies_costs(
                electric_consumption,
                thermal_consumption,
                refrigeration_consumption,
                "Cogen",
            )

            # calculation of the best size of trigen, pv, battery
            (
                PV_size_T,
                cogen_size_T,
                trigen_size_T,
                battery_size_T,
                savings_T,
                investment_costs_T,
                total_costs_T,
                percentage_energy_coverage_T,
            ) = multivector_controller_wrapped_functions.sizes_energies_costs(
                electric_consumption,
                thermal_consumption,
                refrigeration_consumption,
                "Trigen",
            )
            # choose between cogen or trigen
            if (
                total_costs_C < total_costs_T
            ):  # the cost of cogen are less then trigen -> choose cogen
                PV_size = PV_size_C
                cogen_size = cogen_size_C
                cogen_trigen_size = cogen_size
                trigen_size = trigen_size_C
                battery_size = battery_size_C
                savings = savings_C
                investment_costs = investment_costs_C
                LabelCogTrigen = "Cogen"

            else:  # the cost of trigen are less then cogen -> choose trigen
                PV_size = PV_size_T
                cogen_size = cogen_size_T
                trigen_size = trigen_size_T
                cogen_trigen_size = trigen_size
                battery_size = battery_size_T
                savings = savings_T
                investment_costs = investment_costs_T
                LabelCogTrigen = "Trigen"

            # calculation of recovery time
            recovery_time = model.calc_payback_time(savings, investment_costs)

            # SEE RESULTS
            user_output.see_optimal_sizes(
                PV_size, cogen_size, trigen_size, battery_size
            )

            user_output.see_costs_investment_recovery(investment_costs, recovery_time)

            # GRAPH WITH ENERGY PRODUCTION AND CONSUMPTION

            if "period_label" not in st.session_state:
                st.session_state["period_label"] = None
            st.session_state["period_label"] = user_input.select_period_plot()

            if st.session_state["period_label"] is not None:
                period_to_be_plot = user_output.extract_period_from_period_label(
                    st.session_state["period_label"]
                )
                electric_consumption_period = model.calculate_mean_over_period(
                    electric_consumption, period_to_be_plot
                )
                electric_production_pv = model.calculation_pv_production(PV_size)
                (
                    electric_production_cogen,
                    thermal_production_cogen,
                    refrigeration_production_cogen,
                ) = model.annual_production_cogen_trigen(
                    cogen_trigen_size, LabelCogTrigen
                )
                electric_production_period = model.calculate_mean_over_period(
                    np.nansum(
                        [electric_production_cogen, electric_production_pv], axis=0
                    ),
                    period_to_be_plot,
                )
                user_output.see_coverage_energy_plot(
                    electric_consumption_period,
                    electric_production_period,
                    "Elettrica",
                    st.session_state["period_label"],
                )

                if np.nansum(thermal_production_cogen) > 0:
                    thermal_production_cogen_period = model.calculate_mean_over_period(
                        thermal_production_cogen, period_to_be_plot
                    )
                    thermal_consumption_period = model.calculate_mean_over_period(
                        thermal_consumption, period_to_be_plot
                    )
                    user_output.see_coverage_energy_plot(
                        thermal_consumption_period,
                        thermal_production_cogen_period,
                        "Termica",
                        st.session_state["period_label"],
                    )

                if np.nansum(refrigeration_production_cogen) > 0:
                    refrigeration_consumption_period = model.calculate_mean_over_period(
                        refrigeration_consumption, period_to_be_plot
                    )
                    refrigeration_production_period = model.calculate_mean_over_period(
                        refrigeration_production_cogen, period_to_be_plot
                    )
                    user_output.see_coverage_energy_plot(
                        refrigeration_consumption_period,
                        refrigeration_production_period,
                        "Frigorifera",
                        st.session_state["period_label"],
                    )
