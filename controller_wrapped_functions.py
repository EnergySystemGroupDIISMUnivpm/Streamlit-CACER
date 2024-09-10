import datetime

from numpy import power
from pydantic import PositiveFloat, validate_call
from cacer_simulator.views.view import UserInput, Results
from cacer_simulator.models import model
import cacer_simulator.common as common


def info_pv_or_area(
    user_input,
) -> tuple[int | None, datetime.date | None, int | None, int | None]:
    """
    ask to user if has an area or PV plant. if has area ask dimenstion. if has PV plant, ask year, power and boosting power.
    """
    area = None
    year_pv = None
    power_pv = None
    add_power = None
    has_pv_or_area = user_input.pv_or_area()
    if has_pv_or_area == "Ho un'area in cui costruirlo":
        area = user_input.insert_area()
    elif has_pv_or_area == "Ho già un impianto":
        year_pv, power_pv = user_input.insert_year_power_PV()
        add_power = user_input.boosting_power()
    return area, year_pv, power_pv, add_power


@validate_call
def results_from_PV_power(
    label_use_case: common.LabelUseCaseType,
    label_pv_or_area: common.LabelPVAreaType,
    power_pv: PositiveFloat,
    consumption: common.PositiveOrZeroFloat,
    percentage_daily_consumption: common.PercentageType,
    region: common.RegionType,
    year_pv: datetime.date,
    results: Results,
    inhabitants="No",
    add_power=0,
):
    """
    calculation and visualization of the CACER simulation results.
    """

    result_view = results.see_results()
    if result_view:

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
        # case of CER
        if label_use_case == "CER":
            results_CER(
                energy_self_consump,
                production,
                label_pv_or_area,
                power_pv,
                consumption,
                percentage_daily_consumption,
                region,
                year_pv,
                results,
                overproduction_or_undeproduction,
                energy_difference_produc_consum,
                inhabitants,
                add_power,
            )
        # case of Self_consumer and Group
        else:
            benefit_results(
                energy_self_consump,
                production,
                label_use_case,
                label_pv_or_area,
                power_pv,
                consumption,
                percentage_daily_consumption,
                region,
                year_pv,
                results,
                inhabitants,
                add_power,
            )
            presence_overproduction_or_undeproduction(
                label_use_case,
                overproduction_or_undeproduction,
                results,
                consumption,
                region,
                percentage_daily_consumption,
                power_pv,
            )


@validate_call
def presence_overproduction_or_undeproduction(
    label_use_case: common.LabelUseCaseType,
    overproduction_or_undeproduction: common.LabelOverproUnderprodType,
    results: Results,
    consumption: PositiveFloat,
    region: common.RegionType,
    percentage_daily_consumption: common.PercentageType,
    power_pv: PositiveFloat,
):
    """
    determitaion of overproduction or undeproduction and visualization of relative results. For Self_consumer and Group.
    """
    # case of overproduction, so there is visualization of advice for creating a CER
    if overproduction_or_undeproduction == "Overproduction":
        results.visualize_advices()
        results.see_CER_info(label_use_case)
    # case of underproduction, so there is visualization of advice for boosting PV plant.
    elif overproduction_or_undeproduction == "Underproduction":
        results.visualize_advices()
        optimal_PV_size = model.optimal_sizing(
            consumption,
            region,
            percentage_daily_consumption,
        )
        results.see_optimal_size(optimal_PV_size)
        cost_plants = model.compute_cost_plant(optimal_PV_size - power_pv)
        results.see_computed_costs_plant(cost_plants, "Potenziamento")


@validate_call
def benefit_results(
    energy_self_consump: PositiveFloat,
    production: PositiveFloat,
    label_use_case: common.LabelUseCaseType,
    label_pv_or_area: common.LabelPVAreaType,
    power_pv: PositiveFloat,
    consumption: PositiveFloat,
    percentage_daily_consumption: common.PercentageType,
    region: common.RegionType,
    year_pv: datetime.date,
    results: Results,
    inhabitants="No",
    add_power=0,
):
    """
    computation and visualization of economical and environmental benefits. For Self_consumer and Group.
    """
    results.visualize_useful_information()
    # only when user has area
    if label_pv_or_area == "area":
        results.see_installable_power(power_pv)
        cost_plant = model.compute_cost_plant(power_pv)
        results.see_computed_costs_plant(cost_plant, "Creazione")
    # both for area and PV plant already present
    results.see_production(production, label_pv_or_area)
    results.visualize_economical_environmental_benefits()
    benefit_b = model.economical_benefit_b(
        power_pv,
        year_pv,
        add_power,
        region,
        energy_self_consump,
    )
    environmental_benefit = model.environmental_benefits(energy_self_consump)
    results.see_economical_benefit_b(
        benefit_b,
    )

    results.see_environmental_benefit(
        environmental_benefit,
    )
    # benefit a only for Group (benefit a is not obternable for Self_consumer. Benefit a is on construction of PV (boosting part or new PV)
    if label_use_case == "Group":
        if inhabitants == "Si":
            # case of PV already present. benefit a is calculated only on the boosting power.
            if label_pv_or_area == "PV" and add_power > 0:
                benefit_a = model.economical_benefit_a(power_pv + add_power, add_power)
                results.see_economical_benefit_a(benefit_a)  # type: ignore
            # case of area. benefit a is calculated on the entire new possible installable PV plant.
            elif label_pv_or_area == "area":
                benefit_a = model.economical_benefit_a(power_pv)
                results.see_economical_benefit_a(benefit_a)  # type: ignore


@validate_call
def results_CER(
    energy_self_consump: PositiveFloat,
    production: PositiveFloat,
    label_pv_or_area: common.LabelPVAreaType,
    power_pv: PositiveFloat,
    consumption: PositiveFloat,
    percentage_daily_consumption: common.PercentageType,
    region: common.RegionType,
    year_pv: datetime.date,
    results: Results,
    overproduction_or_undeproduction: common.LabelOverproUnderprodType,
    energy_difference_produc_consum: float,
    inhabitants="No",
    add_power=0,
):
    """
    computation and visualization of results only for CER.
    """
    # for both area and PV
    results.visualize_useful_information()
    # only for case in which user has area
    if label_pv_or_area == "area":
        results.see_installable_power(power_pv)
        cost_plant = model.compute_cost_plant(power_pv)
        results.see_computed_costs_plant(cost_plant, "Creazione")

    results.see_production(production, label_pv_or_area)

    # case of Overproduction. So new possible members of CER are proposed with relative economical and environmental benefits.
    if overproduction_or_undeproduction == "Overproduction":
        optimal_members = model.optimal_members(energy_difference_produc_consum)
        results.visualize_advices()
        results.see_optimal_members(optimal_members, "membri già presenti")

        benefit_b_present_members = model.economical_benefit_b(
            power_pv,
            year_pv,
            add_power,
            region,
            energy_self_consump,
        )
        benefit_b_added_members = model.economical_benefit_b(
            power_pv,
            year_pv,
            add_power,
            region,
            production,
        )

        environmental_benefit_present_members = model.environmental_benefits(
            energy_self_consump
        )
        environmental_benefit_added_members = model.environmental_benefits(production)

        results.visualize_economical_environmental_benefits()
        # benefit a (only of inhabitants < 5000)
        if inhabitants == "Si" and add_power > 0:
            # case of PV already present. benefit a is calculated only on the boosting power.
            if label_pv_or_area == "PV":
                benefit_a = model.economical_benefit_a(power_pv + add_power, add_power)
                # case of area. benefit a is calculated on entrire possible installable PV plant.
            elif label_pv_or_area == "area":
                benefit_a = model.economical_benefit_a(power_pv + add_power, add_power)

            results.see_economical_benefit_a(
                benefit_a,  # type: ignore
            )
        results.see_economical_benefit_b(
            benefit_b_present_members,
            benefit_b_added_members,
        )

        results.see_environmental_benefit(
            environmental_benefit_present_members,
            environmental_benefit_added_members,
        )
    # case of unserproduction so the optimal dimension of PV plant is proosed.
    elif overproduction_or_undeproduction == "Underproduction":
        optimal_PV_size = model.optimal_sizing(
            consumption,
            region,
            percentage_daily_consumption,
        )

        results.visualize_advices()

        results.see_optimal_size(optimal_PV_size)
        cost_plant = model.compute_cost_plant(optimal_PV_size - power_pv)
        results.see_computed_costs_plant(cost_plant, "Potenziamento")

        benefit_b_present_members = model.economical_benefit_b(
            power_pv,
            year_pv,
            add_power,
            region,
            energy_self_consump,
        )

        environmental_benefit_present_members = model.environmental_benefits(
            energy_self_consump
        )

        results.visualize_economical_environmental_benefits()
        # benefit a (only for inhabitants < 5000)
        if inhabitants == "Si" and add_power > 0:
            benefit_a = model.economical_benefit_a(power_pv + add_power, add_power)

            results.see_economical_benefit_a(benefit_a)

        results.see_economical_benefit_b(benefit_b_present_members)

        results.see_environmental_benefit(environmental_benefit_present_members)

    # case of optimal dimension of PV plant. Results are simply visualized.
    elif overproduction_or_undeproduction == "Optimal":

        benefit_b_present_members = model.economical_benefit_b(
            power_pv,
            year_pv,
            add_power,
            region,
            energy_self_consump,
        )

        environmental_benefit_present_members = model.environmental_benefits(
            energy_self_consump
        )
        results.visualize_economical_environmental_benefits()
        # benefit a (only for inhabitants < 5000)
        if inhabitants == "Si" and add_power > 0:
            # case of PV already present. benefit a is calculated only on the boosting power.
            if label_pv_or_area == "PV":
                benefit_a = model.economical_benefit_a(power_pv + add_power, add_power)
            # case of area. benefit a is calculated on entrire possible installable PV plant.
            elif label_pv_or_area == "area":
                benefit_a = model.economical_benefit_a(power_pv + add_power, add_power)

            results.see_economical_benefit_a(benefit_a)  # type: ignore

        results.see_economical_benefit_b(benefit_b_present_members)

        results.see_environmental_benefit(environmental_benefit_present_members)
