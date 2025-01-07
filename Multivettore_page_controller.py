from math import e
from tracemalloc import start
import streamlit as st
import pandas as pd
from multivector_simulator.views.view import UserInput, UserOuput, title_multivettore
from multivector_simulator.models import model
import numpy as np
import multivector_simulator.common as common
import multivector_controller_wrapped_functions
import calcoli_validazione


def Simulator_Multivettore():
    title_multivettore()
    user_input = UserInput()
    start_winter_season = 10  # Nov
    end_winter_season = 2  # March
    electric_consumption = None
    thermal_consumption = None
    refrigeration_consumption = None
    consumption = user_input.download_upload_consumption()
    user_output = UserOuput()
    if "electric_consumption" not in st.session_state:
        st.session_state["electric_consumption"] = None
    if "thermal_consumption" not in st.session_state:
        st.session_state["thermal_consumption"] = None
    if "refrigeration_consumption" not in st.session_state:
        st.session_state["refrigeration_consumption"] = None

    tot_electric_consum = None
    tot_thermal_consum = None
    tot_refrig_consum = None
    tot_electric_consum, tot_thermal_consum, tot_refrig_consum = (
        UserInput().insert_annual_consumption()
    )
    if all(
        x is not None
        for x in (tot_electric_consum, tot_thermal_consum, tot_refrig_consum)
    ):  # type:ignore
        (
            st.session_state["electric_consumption"],
            st.session_state["thermal_consumption"],
            st.session_state["refrigeration_consumption"],
        ) = model.simulation_electric_themal_refrig_consumption_profile(
            tot_electric_consum,  # type: ignore
            tot_thermal_consum,  # type:ignore
            tot_refrig_consum,  # type:ignore
        )

    # Load consumption
    elif consumption is not None:
        st.session_state["electric_consumption"] = consumption[
            "Consumi Elettrici (kWh)"
        ].to_numpy()
        st.session_state["thermal_consumption"] = consumption[
            "Consumi Termici (kWh)"
        ].to_numpy()
        st.session_state["refrigeration_consumption"] = consumption[
            "Consumi Frigoriferi (kWh)"
        ].to_numpy()

    if all(
        x is not None
        for x in (
            st.session_state["electric_consumption"],
            st.session_state["thermal_consumption"],
            st.session_state["refrigeration_consumption"],
        )
    ):  # type:ignore
        electric_consumption = st.session_state["electric_consumption"]
        thermal_consumption = st.session_state["thermal_consumption"]
        refrigeration_consumption = st.session_state["refrigeration_consumption"]
        if refrigeration_consumption.any() != 0:  # type:ignore
            LabelCogTrigen = "Trigen"
        else:
            LabelCogTrigen = "Cogen"
        # Insert button results
        if "see_results" not in st.session_state:
            st.session_state["see_results"] = False

        if not st.session_state["see_results"]:
            if user_output.see_results():
                st.session_state["see_results"] = True

        if st.session_state["see_results"]:
            # calculation of the best size of cogen/trigen, pv, battery
            (
                PV_size,
                cogen_size,
                trigen_size,
                battery_size,
                savings,
                investment_costs,
                cost_gas,
            ) = multivector_controller_wrapped_functions.sizes_energies_costs(
                electric_consumption,
                thermal_consumption,
                refrigeration_consumption,
                LabelCogTrigen,
                start_winter_season,
                end_winter_season,
            )
            if LabelCogTrigen == "Cogen":
                cogen_trigen_size = cogen_size
            else:
                cogen_trigen_size = trigen_size

            # cost of maintenance of PV and cogen/trigen in a year
            annual_maintenance_cost = model.maintenance_cost_PV(
                PV_size, battery_size
            ) + model.maintenance_cost_cogen_trigen(cogen_trigen_size, LabelCogTrigen)

            # calculation of recovery time
            df_cumulative_cost_savings = model.cumulative_costs_savings(
                savings, investment_costs, cost_gas + annual_maintenance_cost
            )
            recovery_time = model.calc_payback_time(df_cumulative_cost_savings)

            # SEE RESULTS
            user_output.see_optimal_sizes(
                PV_size, cogen_size, trigen_size, battery_size
            )

            user_output.see_costs_investment_recovery(investment_costs, recovery_time)
            user_output.graph_return_investment(df_cumulative_cost_savings)

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
                    cogen_trigen_size,
                    LabelCogTrigen,
                    start_winter_season,
                    end_winter_season,
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
