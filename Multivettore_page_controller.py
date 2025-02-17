from math import e
from tracemalloc import start
from requests import session
import streamlit as st
import pandas as pd
from multivector_simulator.views.view import (
    UserInput,
    UserOuput,
    title_multivettore,
    KnwonProfileConsump_or_Total,
)
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
    if "electric_consumption" not in st.session_state:
        st.session_state["electric_consumption"] = None
    if "thermal_consumption" not in st.session_state:
        st.session_state["thermal_consumption"] = None
    if "refrigeration_consumption" not in st.session_state:
        st.session_state["refrigeration_consumption"] = None
    tot_electric_consum = None
    tot_thermal_consum = None
    tot_refrig_consum = None
    profileConsump_or_onlyTotal = user_input.select_profileConsump_or_onlyTotal()
    match profileConsump_or_onlyTotal:
        case KnwonProfileConsump_or_Total.KnwonProfileConsump:
            consumption = user_input.download_upload_consumption()
            if consumption is not None:
                st.session_state["electric_consumption"] = consumption[
                    "Consumi Elettrici (kWh)"
                ].to_numpy()
                st.session_state["thermal_consumption"] = consumption[
                    "Consumi Termici (kWh)"
                ].to_numpy()
                st.session_state["refrigeration_consumption"] = consumption[
                    "Consumi Frigoriferi (kWh)"
                ].to_numpy()
                electric_consumption = st.session_state["electric_consumption"]
                thermal_consumption = st.session_state["thermal_consumption"]
                refrigeration_consumption = st.session_state[
                    "refrigeration_consumption"
                ]
        case KnwonProfileConsump_or_Total.KnwonTotalConsump:
            tot_electric_consum, tot_thermal_consum, tot_refrig_consum = (
                UserInput().insert_annual_consumption()
            )
            if all(
                x is not None
                for x in [tot_electric_consum, tot_thermal_consum, tot_refrig_consum]
            ):
                (
                    st.session_state["electric_consumption"],
                    st.session_state["thermal_consumption"],
                    st.session_state["refrigeration_consumption"],
                ) = model.simulation_electric_themal_refrig_consumption_profile(
                    tot_electric_consum,  # type: ignore
                    tot_thermal_consum,  # type:ignore
                    tot_refrig_consum,  # type:ignore
                )
    user_output = UserOuput()
    electric_consumption = st.session_state["electric_consumption"]
    thermal_consumption = st.session_state["thermal_consumption"]
    refrigeration_consumption = st.session_state["refrigeration_consumption"]
    if all(
        x is not None
        for x in [electric_consumption, thermal_consumption, refrigeration_consumption]
    ):
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

        if "PV_size" not in st.session_state:
            st.session_state["PV_size"] = None
        if "cogen_size" not in st.session_state:
            st.session_state["cogen_size"] = None
        if "trigen_size" not in st.session_state:
            st.session_state["trigen_size"] = None
        if "battery_size" not in st.session_state:
            st.session_state["battery_size"] = None
        if "cogen_trigen_size" not in st.session_state:
            st.session_state["cogen_trigen_size"] = None

        if st.session_state["see_results"]:
            recovery_time = common.Optimizer().YEARS + 1
            attempts = 0
            found_result = False
            while recovery_time >= common.Optimizer().YEARS:
                if attempts > common.Optimizer().ATTEMPTS:
                    user_output.no_result_found()
                    break
                # calculation of the best size of cogen/trigen, pv, battery
                with st.spinner(
                    "Elaborazione in corso... Il processo potrebbe richiedere alcuni minuti. Non chiudere la pagina."
                ):
                    (
                        st.session_state["PV_size"],
                        st.session_state["cogen_size"],
                        st.session_state["trigen_size"],
                        st.session_state["battery_size"],
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
                    st.session_state["cogen_trigen_size"] = st.session_state[
                        "cogen_size"
                    ]
                else:
                    st.session_state["cogen_trigen_size"] = st.session_state[
                        "trigen_size"
                    ]

                # cost of maintenance of PV and cogen/trigen in a year
                annual_maintenance_cost = model.maintenance_cost_PV(
                    st.session_state["PV_size"], st.session_state["battery_size"]
                ) + model.maintenance_cost_cogen_trigen(
                    st.session_state["cogen_trigen_size"], LabelCogTrigen
                )

                # calculation of recovery time

                df_cumulative_cost_savings = model.cumulative_costs_savings(
                    savings, investment_costs, cost_gas + annual_maintenance_cost
                )
                recovery_time = model.calc_payback_time(df_cumulative_cost_savings)
                if recovery_time < common.Optimizer().YEARS:
                    found_result = True  # Risultato trovato
                    break  # Uscita dal ciclo
                attempts += 1

            # SEE RESULTS
            if found_result == True:
                user_output.see_optimal_sizes(
                    st.session_state["PV_size"],
                    st.session_state["cogen_size"],
                    st.session_state["trigen_size"],
                    st.session_state["battery_size"],
                )

                user_output.see_costs_investment_recovery(
                    investment_costs, recovery_time
                )  # type:ignore
                user_output.graph_return_investment(
                    df_cumulative_cost_savings
                )  # type:ignore

                # GRAPH WITH ENERGY PRODUCTION AND CONSUMPTION
                electric_production_pv = model.calculation_pv_production(
                    st.session_state["PV_size"]
                )
                electric_production_pv = model.calculation_pv_production(
                    st.session_state["PV_size"]
                )
                (
                    electric_production_cogen,
                    thermal_production_cogen,
                    refrigeration_production_cogen,
                ) = model.annual_production_cogen_trigen(
                    st.session_state["cogen_trigen_size"],
                    LabelCogTrigen,
                    start_winter_season,
                    end_winter_season,
                )

                user_output.info_andamento_tipico()
                for period in common.PERIOD_TO_BE_PLOTTED.keys():
                    st.session_state["period_label"] = period
                    period_to_be_plot = user_output.extract_period_from_period_label(
                        st.session_state["period_label"]
                    )
                    electric_consumption_period = model.calculate_mean_over_period(
                        electric_consumption, period_to_be_plot
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
                        thermal_production_cogen_period = (
                            model.calculate_mean_over_period(
                                thermal_production_cogen, period_to_be_plot
                            )
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
                        refrigeration_consumption_period = (
                            model.calculate_mean_over_period(
                                refrigeration_consumption, period_to_be_plot
                            )
                        )
                        refrigeration_production_period = (
                            model.calculate_mean_over_period(
                                refrigeration_production_cogen, period_to_be_plot
                            )
                        )
                        user_output.see_coverage_energy_plot(
                            refrigeration_consumption_period,
                            refrigeration_production_period,
                            "Frigorifera",
                            st.session_state["period_label"],
                        )
