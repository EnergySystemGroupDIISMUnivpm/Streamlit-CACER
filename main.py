import streamlit as st
import datetime
from cacer_simulator.views.homepage import MacroGroup, show_macro_group_selector
from cacer_simulator.views.view import UserInput, Results
import controller_functions
from cacer_simulator.models import model


def main():
    choice = show_macro_group_selector()

    match choice:
        case MacroGroup.AutoconsumatoreADistanza:
            st.toast("SELECTED: Autoconsumatore a distanza", icon="💡")
            user_input = UserInput()
            results = Results()
            region = user_input.insert_region()
            consumption = user_input.insert_annual_consumption(
                "Inserisci il tuo consumo annuo in kWh"
            )
            percentage_daily_consumption = (
                user_input.insert_percentage_daytime_consumption()
            )
            area, year_pv, power_pv, add_power = controller_functions.info_pv_or_area(
                user_input
            )
            if region and percentage_daily_consumption and consumption:
                if power_pv and year_pv:
                    if add_power is not None:  # va bene anche se è 0
                        production = model.production_estimate(
                            power_pv + add_power, region
                        )
                        energy_self_consump = model.estimate_self_consumed_energy(
                            consumption, percentage_daily_consumption, production
                        )
                        diurnal_consum = percentage_daily_consumption * consumption
                        energy_difference_produc_consum = model.energy_difference(
                            diurnal_consum, production
                        )
                        overproduction_or_undeproduction = (
                            model.presence_of_overproduction_or_underproduction(
                                energy_difference_produc_consum, region
                            )
                        )

                        result_view = results.see_results()

                        if result_view:
                            results.see_production(production, "PV")
                            benefit_b = model.economical_benefit_b(
                                power_pv,
                                year_pv,
                                add_power,
                                region,
                                energy_self_consump,
                            )
                            environmental_benefit = model.environmental_benefits(
                                energy_self_consump
                            )

                            results.see_economical_benefit_b(
                                benefit_b,
                            )

                            results.see_environmental_benefit(
                                environmental_benefit,
                            )

                            if overproduction_or_undeproduction == "Overproduction":
                                results.see_CER_info()

                            elif overproduction_or_undeproduction == "Underproduction":
                                optimal_PV_size = model.optimal_sizing(
                                    consumption,
                                    region,
                                    percentage_daily_consumption,
                                )

                                results.see_optimal_size(optimal_PV_size)
                elif area:
                    add_power = 0
                    year_pv = datetime.date.today()
                    power_pv = model.computation_installable_power(area)
                    production = model.production_estimate(power_pv + add_power, region)
                    energy_self_consump = model.estimate_self_consumed_energy(
                        consumption, percentage_daily_consumption, production
                    )
                    diurnal_consum = percentage_daily_consumption * consumption
                    energy_difference_produc_consum = model.energy_difference(
                        diurnal_consum, production
                    )
                    overproduction_or_undeproduction = (
                        model.presence_of_overproduction_or_underproduction(
                            energy_difference_produc_consum, region
                        )
                    )

                    result_view = results.see_results()

                    if result_view:
                        results.see_installable_power(power_pv)
                        results.see_production(production, "area")
                        benefit_b = model.economical_benefit_b(
                            power_pv,
                            year_pv,
                            add_power,
                            region,
                            energy_self_consump,
                        )
                        environmental_benefit = model.environmental_benefits(
                            energy_self_consump
                        )

                        results.see_economical_benefit_b(
                            benefit_b,
                        )

                        results.see_environmental_benefit(
                            environmental_benefit,
                        )

                        if overproduction_or_undeproduction == "Overproduction":
                            results.see_CER_info()

                        elif overproduction_or_undeproduction == "Underproduction":
                            optimal_PV_size = model.optimal_sizing(
                                consumption,
                                region,
                                percentage_daily_consumption,
                            )

                            results.see_optimal_size(optimal_PV_size)

        case MacroGroup.ComunitaEnergetica:
            st.toast("SELECTED: Comunità Energetica", icon="💡")
            user_input = UserInput()
            results = Results()
            region = user_input.insert_region()
            inhabitants = user_input.municipality()
            know_cer_members = user_input.cer_with()
            if know_cer_members == "Si":
                knowledge_cer_consumption = user_input.know_members_consumption("CER")
                if knowledge_cer_consumption == "No" and region:
                    members = user_input.insert_members("CER")
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
                            diurnal_consum = percentage_daily_consumption * consumption
                            energy_difference_produc_consum = model.energy_difference(
                                diurnal_consum, production
                            )
                            overproduction_or_undeproduction = (
                                model.presence_of_overproduction_or_underproduction(
                                    energy_difference_produc_consum, region
                                )
                            )

                            result_view = results.see_results()

                            if result_view:
                                results.see_production(production, "PV")
                                if overproduction_or_undeproduction == "Overproduction":
                                    optimal_members = model.optimal_members(
                                        energy_difference_produc_consum
                                    )

                                    benefit_b_present_members = (
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

                                    environmental_benefit_present_members = (
                                        model.environmental_benefits(
                                            energy_self_consump
                                        )
                                    )
                                    environmental_benefit_added_members = (
                                        model.environmental_benefits(production)
                                    )
                                    results.see_optimal_members(
                                        optimal_members, "membri già presenti"
                                    )
                                    if inhabitants == "Si":
                                        benefit_a = model.economical_benefit_a(
                                            add_power
                                        )

                                        results.see_economical_benefit_a(
                                            benefit_a,
                                        )
                                    results.see_economical_benefit_b(
                                        benefit_b_present_members,
                                        benefit_b_added_members,
                                    )

                                    results.see_environmental_benefit(
                                        environmental_benefit_present_members,
                                        environmental_benefit_added_members,
                                    )

                                elif (
                                    overproduction_or_undeproduction
                                    == "Underproduction"
                                ):
                                    optimal_PV_size = model.optimal_sizing(
                                        consumption,
                                        region,
                                        percentage_daily_consumption,
                                    )

                                    benefit_b_present_members = (
                                        model.economical_benefit_b(
                                            power_pv,
                                            year_pv,
                                            add_power,
                                            region,
                                            energy_self_consump,
                                        )
                                    )

                                    environmental_benefit_present_members = (
                                        model.environmental_benefits(
                                            energy_self_consump
                                        )
                                    )

                                    if inhabitants == "Si":
                                        benefit_a = model.economical_benefit_a(
                                            add_power
                                        )

                                        results.see_economical_benefit_a(benefit_a)

                                    results.see_economical_benefit_b(
                                        benefit_b_present_members
                                    )

                                    results.see_environmental_benefit(
                                        environmental_benefit_present_members
                                    )

                                    results.see_optimal_size(optimal_PV_size)
                                elif overproduction_or_undeproduction == "Optimal":

                                    benefit_b_present_members = (
                                        model.economical_benefit_b(
                                            power_pv,
                                            year_pv,
                                            add_power,
                                            region,
                                            energy_self_consump,
                                        )
                                    )

                                    environmental_benefit_present_members = (
                                        model.environmental_benefits(
                                            energy_self_consump
                                        )
                                    )

                                    if inhabitants == "Si":
                                        benefit_a = model.economical_benefit_a(
                                            add_power
                                        )

                                        results.see_economical_benefit_a(benefit_a)

                                    results.see_economical_benefit_b(
                                        benefit_b_present_members
                                    )

                                    results.see_environmental_benefit(
                                        environmental_benefit_present_members
                                    )
                    elif area:
                        add_power = 0
                        year_pv = datetime.date.today()

                        installable_power = model.computation_installable_power(area)
                        production = model.production_estimate(
                            installable_power + add_power, region
                        )
                        percentage_daily_consumption = (
                            model.percentage_daytime_consumption_estimation(members)
                        )
                        energy_self_consump = model.estimate_self_consumed_energy(
                            consumption, percentage_daily_consumption, production
                        )
                        diurnal_consum = percentage_daily_consumption * consumption
                        energy_difference_produc_consum = model.energy_difference(
                            diurnal_consum, production
                        )
                        overproduction_or_undeproduction = (
                            model.presence_of_overproduction_or_underproduction(
                                energy_difference_produc_consum, region
                            )
                        )

                        result_view = results.see_results()

                        if result_view:
                            results.see_installable_power(installable_power)
                            results.see_production(production, "area")
                            if overproduction_or_undeproduction == "Overproduction":
                                optimal_members = model.optimal_members(
                                    energy_difference_produc_consum
                                )

                                benefit_b_present_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    energy_self_consump,
                                )
                                benefit_b_added_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    production,
                                )

                                environmental_benefit_present_members = (
                                    model.environmental_benefits(energy_self_consump)
                                )
                                environmental_benefit_added_members = (
                                    model.environmental_benefits(production)
                                )
                                results.see_optimal_members(
                                    optimal_members, "membri già presenti"
                                )
                                if inhabitants == "Si":
                                    benefit_a = model.economical_benefit_a(
                                        installable_power + add_power
                                    )

                                    results.see_economical_benefit_a(
                                        benefit_a,
                                    )
                                results.see_economical_benefit_b(
                                    benefit_b_present_members,
                                    benefit_b_added_members,
                                )

                                results.see_environmental_benefit(
                                    environmental_benefit_present_members,
                                    environmental_benefit_added_members,
                                )

                            elif overproduction_or_undeproduction == "Underproduction":
                                optimal_PV_size = model.optimal_sizing(
                                    consumption,
                                    region,
                                    percentage_daily_consumption,
                                )

                                benefit_b_present_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    energy_self_consump,
                                )

                                environmental_benefit_present_members = (
                                    model.environmental_benefits(energy_self_consump)
                                )

                                if inhabitants == "Si":
                                    benefit_a = model.economical_benefit_a(
                                        installable_power + add_power
                                    )

                                    results.see_economical_benefit_a(benefit_a)

                                results.see_economical_benefit_b(
                                    benefit_b_present_members
                                )

                                results.see_environmental_benefit(
                                    environmental_benefit_present_members
                                )

                                results.see_optimal_size(optimal_PV_size)
                            elif overproduction_or_undeproduction == "Optimal":

                                benefit_b_present_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    energy_self_consump,
                                )

                                environmental_benefit_present_members = (
                                    model.environmental_benefits(energy_self_consump)
                                )

                                if inhabitants == "Si":
                                    benefit_a = model.economical_benefit_a(
                                        installable_power + add_power
                                    )

                                    results.see_economical_benefit_a(benefit_a)

                                results.see_economical_benefit_b(
                                    benefit_b_present_members
                                )

                                results.see_environmental_benefit(
                                    environmental_benefit_present_members
                                )

                elif knowledge_cer_consumption == "Si" and region:
                    consumption = user_input.insert_annual_consumption(
                        "Inserisci i consumi annui totali, in kwh, della tua CER "
                    )
                    percentage_daily_consumption = (
                        user_input.insert_percentage_daytime_consumption()
                    )
                    area, year_pv, power_pv, add_power = (
                        controller_functions.info_pv_or_area(user_input)
                    )
                    if power_pv and year_pv and percentage_daily_consumption:
                        if add_power is not None:  # va bene anche se è 0
                            production = model.production_estimate(
                                power_pv + add_power, region
                            )

                            energy_self_consump = model.estimate_self_consumed_energy(
                                consumption, percentage_daily_consumption, production
                            )
                            diurnal_consum = percentage_daily_consumption * consumption
                            energy_difference_produc_consum = model.energy_difference(
                                diurnal_consum, production
                            )
                            overproduction_or_undeproduction = (
                                model.presence_of_overproduction_or_underproduction(
                                    energy_difference_produc_consum, region
                                )
                            )

                            result_view = results.see_results()

                            if result_view:
                                results.see_production(production, "PV")
                                if overproduction_or_undeproduction == "Overproduction":
                                    optimal_members = model.optimal_members(
                                        energy_difference_produc_consum
                                    )

                                    benefit_b_present_members = (
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

                                    environmental_benefit_present_members = (
                                        model.environmental_benefits(
                                            energy_self_consump
                                        )
                                    )
                                    environmental_benefit_added_members = (
                                        model.environmental_benefits(production)
                                    )
                                    results.see_optimal_members(
                                        optimal_members, "membri già presenti"
                                    )
                                    if inhabitants == "Si":
                                        benefit_a = model.economical_benefit_a(
                                            add_power
                                        )

                                        results.see_economical_benefit_a(
                                            benefit_a,
                                        )
                                    results.see_economical_benefit_b(
                                        benefit_b_present_members,
                                        benefit_b_added_members,
                                    )

                                    results.see_environmental_benefit(
                                        environmental_benefit_present_members,
                                        environmental_benefit_added_members,
                                    )

                                elif (
                                    overproduction_or_undeproduction
                                    == "Underproduction"
                                ):
                                    optimal_PV_size = model.optimal_sizing(
                                        consumption,
                                        region,
                                        percentage_daily_consumption,
                                    )

                                    benefit_b_present_members = (
                                        model.economical_benefit_b(
                                            power_pv,
                                            year_pv,
                                            add_power,
                                            region,
                                            energy_self_consump,
                                        )
                                    )

                                    environmental_benefit_present_members = (
                                        model.environmental_benefits(
                                            energy_self_consump
                                        )
                                    )

                                    if inhabitants == "Si":
                                        benefit_a = model.economical_benefit_a(
                                            add_power
                                        )

                                        results.see_economical_benefit_a(benefit_a)

                                    results.see_economical_benefit_b(
                                        benefit_b_present_members
                                    )

                                    results.see_environmental_benefit(
                                        environmental_benefit_present_members
                                    )

                                    results.see_optimal_size(optimal_PV_size)
                                elif overproduction_or_undeproduction == "Optimal":

                                    benefit_b_present_members = (
                                        model.economical_benefit_b(
                                            power_pv,
                                            year_pv,
                                            add_power,
                                            region,
                                            energy_self_consump,
                                        )
                                    )

                                    environmental_benefit_present_members = (
                                        model.environmental_benefits(
                                            energy_self_consump
                                        )
                                    )

                                    if inhabitants == "Si":
                                        benefit_a = model.economical_benefit_a(
                                            add_power
                                        )

                                        results.see_economical_benefit_a(benefit_a)

                                    results.see_economical_benefit_b(
                                        benefit_b_present_members
                                    )

                                    results.see_environmental_benefit(
                                        environmental_benefit_present_members
                                    )
                    elif area and percentage_daily_consumption:
                        add_power = 0
                        year_pv = datetime.date.today()

                        installable_power = model.computation_installable_power(area)
                        production = model.production_estimate(
                            installable_power + add_power, region
                        )
                        energy_self_consump = model.estimate_self_consumed_energy(
                            consumption, percentage_daily_consumption, production
                        )
                        diurnal_consum = percentage_daily_consumption * consumption
                        energy_difference_produc_consum = model.energy_difference(
                            diurnal_consum, production
                        )
                        overproduction_or_undeproduction = (
                            model.presence_of_overproduction_or_underproduction(
                                energy_difference_produc_consum, region
                            )
                        )

                        result_view = results.see_results()

                        if result_view:
                            results.see_installable_power(installable_power)
                            results.see_production(production, "area")
                            if overproduction_or_undeproduction == "Overproduction":
                                optimal_members = model.optimal_members(
                                    energy_difference_produc_consum
                                )

                                benefit_b_present_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    energy_self_consump,
                                )
                                benefit_b_added_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    production,
                                )

                                environmental_benefit_present_members = (
                                    model.environmental_benefits(energy_self_consump)
                                )
                                environmental_benefit_added_members = (
                                    model.environmental_benefits(production)
                                )
                                results.see_optimal_members(
                                    optimal_members, "membri già presenti"
                                )
                                if inhabitants == "Si":
                                    benefit_a = model.economical_benefit_a(
                                        installable_power + add_power
                                    )

                                    results.see_economical_benefit_a(
                                        benefit_a,
                                    )
                                results.see_economical_benefit_b(
                                    benefit_b_present_members,
                                    benefit_b_added_members,
                                )

                                results.see_environmental_benefit(
                                    environmental_benefit_present_members,
                                    environmental_benefit_added_members,
                                )

                            elif overproduction_or_undeproduction == "Underproduction":
                                optimal_PV_size = model.optimal_sizing(
                                    consumption,
                                    region,
                                    percentage_daily_consumption,
                                )

                                benefit_b_present_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    energy_self_consump,
                                )

                                environmental_benefit_present_members = (
                                    model.environmental_benefits(energy_self_consump)
                                )

                                if inhabitants == "Si":
                                    benefit_a = model.economical_benefit_a(
                                        installable_power + add_power
                                    )

                                    results.see_economical_benefit_a(benefit_a)

                                results.see_economical_benefit_b(
                                    benefit_b_present_members
                                )

                                results.see_environmental_benefit(
                                    environmental_benefit_present_members
                                )

                                results.see_optimal_size(optimal_PV_size)
                            elif overproduction_or_undeproduction == "Optimal":

                                benefit_b_present_members = model.economical_benefit_b(
                                    installable_power,
                                    year_pv,
                                    add_power,
                                    region,
                                    energy_self_consump,
                                )

                                environmental_benefit_present_members = (
                                    model.environmental_benefits(energy_self_consump)
                                )

                                if inhabitants == "Si":
                                    benefit_a = model.economical_benefit_a(
                                        installable_power + add_power
                                    )

                                    results.see_economical_benefit_a(benefit_a)

                                results.see_economical_benefit_b(
                                    benefit_b_present_members
                                )

                                results.see_environmental_benefit(
                                    environmental_benefit_present_members
                                )

            elif know_cer_members == "No":
                area, year_pv, power_pv, add_power = (
                    controller_functions.info_pv_or_area(user_input)
                )
                if power_pv and year_pv and region:
                    if add_power is not None:  # va bene anche se è 0
                        production = model.production_estimate(
                            power_pv + add_power, region
                        )
                        optimal_members = model.optimal_members(production)
                        result_view = results.see_results()
                        if result_view:
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

                            results.see_optimal_members(
                                optimal_members, "membri non presenti"
                            )
                            if inhabitants == "Si":
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
                        results.see_installable_power(installable_power)
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

                        results.see_optimal_members(
                            optimal_members, "membri non presenti"
                        )
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
            if knowledge_group_consumption == "No" and region:
                members = user_input.insert_members("Group")
                area, year_pv, power_pv, add_power = (
                    controller_functions.info_pv_or_area(user_input)
                )
                consumption = model.consumption_estimation(members)
                ### RICOMINCIARE DA QUI
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
                        diurnal_consum = percentage_daily_consumption * consumption
                        energy_difference_produc_consum = model.energy_difference(
                            diurnal_consum, production
                        )
                        overproduction_or_undeproduction = (
                            model.presence_of_overproduction_or_underproduction(
                                energy_difference_produc_consum, region
                            )
                        )

                        result_view = results.see_results()
                        if result_view:
                            results.see_production(production, "PV")
                            benefit_b = model.economical_benefit_b(
                                power_pv,
                                year_pv,
                                add_power,
                                region,
                                energy_self_consump,
                            )
                            environmental_benefit = model.environmental_benefits(
                                energy_self_consump
                            )
                            results.see_economical_benefit_b(
                                benefit_b,
                            )

                            results.see_environmental_benefit(
                                environmental_benefit,
                            )
                            if inhabitants == "Si":
                                benefit_a = model.economical_benefit_a(add_power)
                                results.see_economical_benefit_a(benefit_a)
                            if overproduction_or_undeproduction == "Overproduction":
                                results.see_CER_info()

                            elif overproduction_or_undeproduction == "Underproduction":
                                optimal_PV_size = model.optimal_sizing(
                                    consumption,
                                    region,
                                    percentage_daily_consumption,
                                )

                                results.see_optimal_size(optimal_PV_size)
                elif area:
                    add_power = 0
                    year_pv = datetime.date.today()
                    power_pv = model.computation_installable_power(area)
                    production = model.production_estimate(power_pv + add_power, region)
                    energy_self_consump = model.estimate_self_consumed_energy(
                        consumption, percentage_daily_consumption, production
                    )
                    diurnal_consum = percentage_daily_consumption * consumption
                    energy_difference_produc_consum = model.energy_difference(
                        diurnal_consum, production
                    )
                    overproduction_or_undeproduction = (
                        model.presence_of_overproduction_or_underproduction(
                            energy_difference_produc_consum, region
                        )
                    )

                    result_view = results.see_results()

                    if result_view:
                        results.see_installable_power(power_pv)
                        results.see_production(production, "area")
                        benefit_b = model.economical_benefit_b(
                            power_pv,
                            year_pv,
                            add_power,
                            region,
                            energy_self_consump,
                        )
                        environmental_benefit = model.environmental_benefits(
                            energy_self_consump
                        )

                        results.see_economical_benefit_b(
                            benefit_b,
                        )

                        results.see_environmental_benefit(
                            environmental_benefit,
                        )

                        if overproduction_or_undeproduction == "Overproduction":
                            results.see_CER_info()

                        elif overproduction_or_undeproduction == "Underproduction":
                            optimal_PV_size = model.optimal_sizing(
                                consumption,
                                region,
                                percentage_daily_consumption,
                            )

                            results.see_optimal_size(optimal_PV_size)


if __name__ == "__main__":
    main()
