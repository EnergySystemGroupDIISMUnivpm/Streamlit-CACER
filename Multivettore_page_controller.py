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

        if not st.session_state["see_results"]:
            if user_output.see_results():
                st.session_state["see_results"] = True

        if st.session_state["see_results"]:

            # OPTIMAL SIZES
            cogen_size = model.calculate_cogen_size_optimized(thermal_consumption)
            (
                PV_size,
                battery_size,
                energy_store_battery_from_cogen,
                self_consump_electric_cogen,
            ) = model.optimizer(eletric_consumption, thermal_consumption)
            energy_store_battery_from_cogen = np.nansum(energy_store_battery_from_cogen)
            self_consump_electric_cogen = np.nansum(self_consump_electric_cogen)

            user_output.see_optimal_sizes(PV_size, cogen_size, battery_size)

            # ENERGY PRODUCED AND SELF-CONSUMED FROM EACH IMPLANT
            eletric_production_cogen, thermal_production_cogen = (
                model.annual_energy_cogen(eletric_consumption, thermal_consumption)
            )
            eletric_production_pv = model.calculation_pv_production(PV_size)

            (
                energy_covered_pv_batteries,
                energy_from_grid,
                self_consumed_energy_battery_pv,
                self_consumed_energy_battery_cogen,
                self_consumed_energy_from_pv,
            ) = model.determination_electric_coverage_year(
                eletric_consumption,
                energy_store_battery_from_cogen,
                PV_size,
                battery_size,
            )
            # calculation of the total energies in a year
            energy_covered_pv_batteries = np.nansum(energy_covered_pv_batteries)
            self_consumed_energy_battery_pv = np.nansum(self_consumed_energy_battery_pv)
            self_consumed_energy_battery_cogen = np.nansum(
                self_consumed_energy_battery_cogen
            )
            self_consumed_energy_from_pv = np.nansum(self_consumed_energy_from_pv)
            energy_from_grid = np.nansum(energy_from_grid)

            total_self_consumed_energy_from_battery = np.nansum(
                [self_consumed_energy_battery_pv, self_consumed_energy_battery_cogen],
                axis=0,
            )
            total_self_consumed_energy_electric = np.nansum(
                [energy_covered_pv_batteries, self_consump_electric_cogen], axis=0
            )
            total_self_consumed_energy_thermal = np.nansum(
                model.energy_self_consumed(
                    thermal_production_cogen, thermal_consumption
                )
            )

            # INVESTIMENTS
            quantity_used_gas_cogen = model.cogen_usage_gas(cogen_size, 24 * 365)
            investment_costs = model.total_cost_investment(
                PV_size, battery_size, cogen_size
            )
            savings = model.savings_using_implants(
                total_self_consumed_energy_electric, total_self_consumed_energy_thermal
            ) - model.cost_gas_used_cogen(quantity_used_gas_cogen)

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
                    eletric_consumption, period_to_be_plot
                )
                electric_production_period = model.calculate_mean_over_period(
                    np.nansum(
                        [eletric_production_cogen, eletric_production_pv], axis=0
                    ),
                    period_to_be_plot,
                )
                user_output.see_coverage_energy_plot(
                    electric_consumption_period,
                    electric_production_period,
                    "Elettrica",
                    st.session_state["period_label"],
                )

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
