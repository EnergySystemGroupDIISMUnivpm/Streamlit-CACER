import streamlit as st

from cacer_simulator.views.homepage import MacroGroup, show_macro_group_selector
from cacer_simulator.views.view import UserInput, Results
import controller_functions
from cacer_simulator.models import model


def main():
    choice = show_macro_group_selector()

    match choice:
        case MacroGroup.AutoconsumatoreADistanza:
            st.toast("SELECTED: Autoconsumatore a distanza", icon="💡")
        case MacroGroup.ComunitaEnergetica:
            st.toast("SELECTED: Comunità Energetica", icon="💡")
            user_input = UserInput()
            results = Results()
            region = user_input.insert_region()
            inhabitants = user_input.municipality()
            know_cer_members = user_input.cer_with()
            if know_cer_members == "Si":
                knowledge_cer_consumption = user_input.know_members_consumption()
                if knowledge_cer_consumption == "No" and region:
                    members = user_input.insert_members()
                    area, year_pv, power_pv, add_power = (
                        controller_functions.info_pv_or_area(user_input)
                    )
                    consumption = model.consumption_estimation(members)
                    if power_pv and year_pv:
                        if add_power is not None:  # va bene anche se è 0
                            production = model.production_estimate(
                                power_pv + add_power, region
                            )
                            percentage_daily_consumption = (
                                model.percentage_daytime_consumption_estimation(members)
                            )
                            energy_self_consump = model.estimate_self_consumed_energy(
                                consumption, percentage_daily_consumption, production
                            )
                            energy_difference_produc_consum = model.energy_difference(
                                energy_self_consump, production
                            )
                            overproduction_or_undeprodcution = (
                                model.presence_of_overproduction_or_underproduction(
                                    energy_difference_produc_consum, region
                                )
                            )
                            result_view = results.see_results()
                            if result_view:
                                results.see_production(production)
                                if overproduction_or_undeprodcution == "Overproduction":
                                    optimal_members = model.optimal_members(
                                        energy_difference_produc_consum
                                    )
                                    benefit_b_present_memebers = (
                                        model.economical_benefit_b(
                                            power_pv,
                                            year_pv,
                                            add_power,
                                            region,
                                            energy_self_consump,
                                        )
                                    )
                                    benefit_b_added_members = (
                                        model.economical_benefit_b(
                                            power_pv,
                                            year_pv,
                                            add_power,
                                            region,
                                            production,
                                        )
                                    )
                                    results.see_optimal_members(
                                        optimal_members, "membri già presenti"
                                    )

                elif knowledge_cer_consumption == "Si":
                    consumption = user_input.insert_annual_consumption(
                        "Inserisci i consumi annui totali, in kwh, della tua CER "
                    )
                    percentage_daily_consumption = (
                        user_input.insert_percentage_daytime_consumption()
                    )
                    area, year_pv, power_pv, add_power = (
                        controller_functions.info_pv_or_area(user_input)
                    )
            elif know_cer_members == "No":
                area, year_pv, power_pv, add_power = (
                    controller_functions.info_pv_or_area(user_input)
                )
        case MacroGroup.GruppoAutoconsumo:
            st.toast("SELECTED: Gruppo Autoconsumo", icon="💡")


if __name__ == "__main__":
    main()
