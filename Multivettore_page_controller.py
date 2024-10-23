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

            # OPTIMAL SIZES
            (PV_size, battery_size, cogen_size) = model.optimizer(
                electric_consumption,
                thermal_consumption,
                refrigeration_consumption,
                "Cogen",
            )

            trigen_size = 0
            user_output.see_optimal_sizes(
                PV_size, cogen_size, trigen_size, battery_size
            )

            (
                electric_energy_from_grid,
                thermal_energy_from_grid,
                refrigeration_energy_from_grid,
                self_consumption_electric_energy_from_cogen_trigen,
                self_consumption_thermal_energy_from_cogen_trigen,
                self_consumption_refrigeration_energy_from_cogen_trigen,
                available_battery_energy_from_cogen_trigen,
            ) = model.calculate_cogen_or_trigen_energy_coverage(
                thermal_consumption,
                refrigeration_consumption,
                electric_consumption,
                cogen_size,
                "Cogen",
            )
            (
                energy_covered_pv_battery,
                energy_from_pv_battery,
                self_consumed_energy_battery_pv,
                self_consumed_energy_battery_cogen,
                self_consumption_electric_energy_from_pv,
            ) = model.determination_electric_coverage_year_PV_battery(
                electric_consumption,
                available_battery_energy_from_cogen_trigen,
                PV_size,
                battery_size,
            )

            # calculation of the total energies in a year
            energy_store_battery_from_cogen_trigen = np.nansum(
                self_consumed_energy_battery_cogen
            )
            total_self_consump_electric_cogen_trigen = np.nansum(
                self_consumption_electric_energy_from_cogen_trigen
            )
            total_self_consumption_electric_energy_from_pv = np.nansum(
                self_consumption_electric_energy_from_pv
            )
            total_self_consumed_energy_from_battery = np.nansum(
                [
                    np.nansum(self_consumed_energy_battery_pv),
                    np.nansum(self_consumed_energy_battery_cogen),
                ],
                axis=0,
            )
            total_self_consumed_energy_electric = np.nansum(
                [
                    total_self_consumed_energy_from_battery,
                    total_self_consump_electric_cogen_trigen,
                    total_self_consumption_electric_energy_from_pv,
                ],
                axis=0,
            )
            total_self_consumed_energy_thermal = np.nansum(
                self_consumption_thermal_energy_from_cogen_trigen
            )
            total_self_consumed_energy_refrigeration = np.nansum(
                self_consumption_refrigeration_energy_from_cogen_trigen
            )

            # INVESTIMENTS

            quantity_used_gas_cogen_trigen = model.cogen_trigen_usage_gas(
                cogen_size, 24 * 365
            )
            investment_costs = model.total_cost_investment(
                PV_size, battery_size, cogen_size, "Cogen"
            )
            savings = model.savings_using_implants(
                total_self_consumed_energy_electric,
                total_self_consumed_energy_thermal,
                total_self_consumed_energy_refrigeration,
            ) - model.cost_gas_used_cogen_trigen(quantity_used_gas_cogen_trigen)

            recovery_time = model.calc_payback_time(savings, investment_costs)
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
                ) = model.annual_production_cogen_trigen(cogen_size, "Cogen")
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
