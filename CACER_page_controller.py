from django import views
import streamlit as st
import datetime
from cacer_simulator.views.macro_selection import (
    MacroGroup,
    show_macro_group_selector,
)
from cacer_simulator.views.view import UserInput, Results, title_CACER
import controller_wrapped_functions
from cacer_simulator.models import model


def Simulator_CACER():
    title_CACER()
    """selection of the type of CACER (CER, Self_consumer, Group)"""
    choice = show_macro_group_selector()

    match choice:
        case MacroGroup.AutoconsumatoreADistanza:
            st.toast("SELECTED: Autoconsumatore a distanza", icon="💡")
            user_input = UserInput()
            results = Results()
            region = user_input.insert_region()
            consumption = user_input.insert_annual_consumption("Self_consumer")
            percentage_daily_consumption = (
                user_input.insert_percentage_daytime_consumption()
            )
            area, year_pv, power_pv, add_power = (
                controller_wrapped_functions.info_pv_or_area(user_input)
            )
            if region and percentage_daily_consumption and consumption:
                # case in which user already has PV plant
                if power_pv and year_pv:
                    if add_power is not None:  # va bene anche se è 0
                        production = model.production_estimate(
                            power_pv + add_power, region
                        )
                        controller_wrapped_functions.results_from_PV_power(
                            "Self_consumer",
                            "PV",
                            power_pv,
                            consumption,
                            percentage_daily_consumption,
                            region,
                            year_pv,
                            results,
                            add_power=add_power,
                        )
                # case in which user has an area in which construct PV plant
                elif area:
                    add_power = 0
                    year_pv = datetime.date.today()
                    power_pv = model.computation_installable_power(area)
                    controller_wrapped_functions.results_from_PV_power(
                        "Self_consumer",
                        "area",
                        power_pv,
                        consumption,
                        percentage_daily_consumption,
                        region,
                        year_pv,
                        results,
                        add_power=add_power,
                    )

        case MacroGroup.ComunitaEnergetica:
            st.toast("SELECTED: Comunità Energetica", icon="💡")
            user_input = UserInput()
            results = Results()
            region = user_input.insert_region()
            inhabitants = user_input.municipality()
            know_cer_members = user_input.cer_with()
            # case in which user knows CER MEMBERS
            if know_cer_members == "Si":
                knowledge_cer_consumption = user_input.know_members_consumption("CER")
                # case in which user does not know the consumption of the members
                if knowledge_cer_consumption == "No" and region:
                    members = user_input.insert_members("CER")
                    percentage_daily_consumption = (
                        model.percentage_daytime_consumption_estimation(members)
                    )
                    area, year_pv, power_pv, add_power = (
                        controller_wrapped_functions.info_pv_or_area(user_input)
                    )
                    consumption = model.consumption_estimation(members)
                    # case in which user has the PV plant
                    if power_pv and year_pv:
                        if add_power is not None:  # va bene anche se è 0
                            controller_wrapped_functions.results_from_PV_power(
                                "CER",
                                "PV",
                                power_pv,
                                consumption,
                                percentage_daily_consumption,
                                region,
                                year_pv,
                                results,
                                inhabitants,  # type: ignore
                                add_power,
                            )
                    # case in which user has the area
                    elif area:
                        add_power = 0
                        year_pv = datetime.date.today()

                        power_pv = model.computation_installable_power(area)
                        percentage_daily_consumption = (
                            model.percentage_daytime_consumption_estimation(members)
                        )
                        controller_wrapped_functions.results_from_PV_power(
                            "CER",
                            "area",
                            power_pv,
                            consumption,
                            percentage_daily_consumption,
                            region,
                            year_pv,
                            results,
                            inhabitants,  # type: ignore
                            add_power,
                        )
                # case in which user knows the consumption of the members
                elif knowledge_cer_consumption == "Si" and region:
                    consumption = user_input.insert_annual_consumption("CER")
                    percentage_daily_consumption = (
                        user_input.insert_percentage_daytime_consumption()
                    )
                    area, year_pv, power_pv, add_power = (
                        controller_wrapped_functions.info_pv_or_area(user_input)
                    )
                    # user has the PV plant
                    if power_pv and year_pv and percentage_daily_consumption:
                        if add_power is not None:  # va bene anche se è 0
                            controller_wrapped_functions.results_from_PV_power(
                                "CER",
                                "PV",
                                power_pv,
                                consumption,
                                percentage_daily_consumption,
                                region,
                                year_pv,
                                results,
                                inhabitants,  # type: ignore
                                add_power,
                            )

                    # user has an area
                    elif area and percentage_daily_consumption:
                        add_power = 0
                        year_pv = datetime.date.today()

                        power_pv = model.computation_installable_power(area)
                        controller_wrapped_functions.results_from_PV_power(
                            "CER",
                            "PV",
                            power_pv,
                            consumption,
                            percentage_daily_consumption,
                            region,
                            year_pv,
                            results,
                            inhabitants,  # type: ignore
                            add_power,
                        )

            # case in which user dosn't know CER members
            elif know_cer_members == "No":
                area, year_pv, power_pv, add_power = (
                    controller_wrapped_functions.info_pv_or_area(user_input)
                )
                # user has PV plant
                if power_pv and year_pv and region:
                    if add_power is not None:  # va bene anche se è 0
                        production = model.production_estimate(
                            power_pv + add_power, region
                        )
                        optimal_members = model.optimal_members(production)
                        result_view = results.see_results()
                        if result_view:
                            results.visualize_useful_information()
                            results.see_production(production, "PV")
                            benefit_b_present_members = model.economical_benefit_b(
                                power_pv,
                                year_pv,
                                add_power,
                                region,
                                production,
                            )
                            environmental_benefit_present_members = (
                                model.environmental_benefits(production)
                            )
                            results.visualize_advices()
                            results.see_optimal_members(
                                optimal_members, "membri non presenti"
                            )
                            results.visualize_economical_environmental_benefits()
                            if inhabitants == "Si" and add_power > 0:
                                benefit_a = model.economical_benefit_a(add_power)

                                results.see_economical_benefit_a(
                                    benefit_a,
                                )
                            results.see_economical_benefit_b(
                                benefit_b_present_members,
                            )

                            results.see_environmental_benefit(
                                environmental_benefit_present_members,
                            )
                # user has area
                if area and region:
                    add_power = 0
                    year_pv = datetime.date.today()
                    installable_power = model.computation_installable_power(area)
                    production = model.production_estimate(
                        installable_power + add_power, region
                    )
                    result_view = results.see_results()
                    if result_view:
                        optimal_members = model.optimal_members(production)
                        results.visualize_useful_information()
                        results.see_installable_power(installable_power)
                        cost_plant = model.compute_cost_plant(installable_power)
                        results.see_computed_costs_plant(cost_plant, "Creazione")
                        results.see_production(production, "area")
                        benefit_b_present_members = model.economical_benefit_b(
                            installable_power,
                            year_pv,
                            add_power,
                            region,
                            production,
                        )
                        environmental_benefit_present_members = (
                            model.environmental_benefits(production)
                        )
                        results.visualize_advices()
                        results.see_optimal_members(
                            optimal_members, "membri non presenti"
                        )
                        results.visualize_economical_environmental_benefits()
                        if inhabitants == "Si":
                            benefit_a = model.economical_benefit_a(
                                installable_power + add_power
                            )

                            results.see_economical_benefit_a(
                                benefit_a,
                            )
                        results.see_economical_benefit_b(
                            benefit_b_present_members,
                        )

                        results.see_environmental_benefit(
                            environmental_benefit_present_members
                        )

        case MacroGroup.GruppoAutoconsumo:
            st.toast("SELECTED: Gruppo Autoconsumo", icon="💡")
            user_input = UserInput()
            results = Results()
            region = user_input.insert_region()
            inhabitants = user_input.municipality()
            knowledge_group_consumption = user_input.know_members_consumption("Group")
            # user doesn't know members consumption
            if knowledge_group_consumption == "No" and region:
                members = user_input.insert_members("Group")
                area, year_pv, power_pv, add_power = (
                    controller_wrapped_functions.info_pv_or_area(user_input)
                )
                consumption = model.consumption_estimation(members)
                percentage_daily_consumption = (
                    model.percentage_daytime_consumption_estimation(members)
                )
                # user has PV plant
                if power_pv and year_pv and inhabitants:
                    if add_power is not None:  # va bene anche se è 0
                        controller_wrapped_functions.results_from_PV_power(
                            "Group",
                            "PV",
                            power_pv,
                            consumption,
                            percentage_daily_consumption,
                            region,
                            year_pv,
                            results,
                            inhabitants,
                            add_power,
                        )
                # user has area
                elif area and inhabitants:
                    add_power = 0
                    year_pv = datetime.date.today()
                    power_pv = model.computation_installable_power(area)
                    controller_wrapped_functions.results_from_PV_power(
                        "Group",
                        "area",
                        power_pv,
                        consumption,
                        percentage_daily_consumption,
                        region,
                        year_pv,
                        results,
                        inhabitants,
                        add_power,
                    )
            # user knows members consumption
            if knowledge_group_consumption == "Si" and region:
                consumption = user_input.insert_annual_consumption("Group")
                percentage_daily_consumption = (
                    user_input.insert_percentage_daytime_consumption()
                )
                area, year_pv, power_pv, add_power = (
                    controller_wrapped_functions.info_pv_or_area(user_input)
                )
                # user has PV plant
                if (
                    power_pv
                    and year_pv
                    and inhabitants
                    and percentage_daily_consumption
                ):
                    if add_power is not None:  # va bene anche se è 0
                        controller_wrapped_functions.results_from_PV_power(
                            "Group",
                            "PV",
                            power_pv,
                            consumption,
                            percentage_daily_consumption,
                            region,
                            year_pv,
                            results,
                            inhabitants,
                            add_power,
                        )
                # user has area
                elif area and inhabitants and percentage_daily_consumption:
                    add_power = 0
                    year_pv = datetime.date.today()
                    power_pv = model.computation_installable_power(area)
                    controller_wrapped_functions.results_from_PV_power(
                        "Group",
                        "area",
                        power_pv,
                        consumption,
                        percentage_daily_consumption,
                        region,
                        year_pv,
                        results,
                        inhabitants,
                        add_power,
                    )
