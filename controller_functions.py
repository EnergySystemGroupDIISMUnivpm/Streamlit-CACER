import datetime

from pydantic import PositiveFloat, validate_call
from cacer_simulator.views.view import UserInput, Results
from cacer_simulator.models import model
import cacer_simulator.common as common


def info_pv_or_area(
    user_input,
) -> tuple[int | None, datetime.date | None, int | None, int | None]:
    area = None
    year_pv = None
    power_pv = None
    add_power = None
    has_pv_or_area = (
        user_input.pv_or_area()
    )  ##si potrebbe evitare di ripeterlo. Da rivedere.
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
    consumption: PositiveFloat,
    percentage_daily_consumption: common.PercentageType,
    region: common.RegionType,
    year_pv: datetime.date,
    results: Results,
    inhabitants="No",
    add_power=0,
):
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
        if label_pv_or_area == "area":
            results.see_installable_power(power_pv)
        results.see_production(production, label_pv_or_area)
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
        if label_use_case == "CER" or label_use_case == "Group":
            if inhabitants == "Si":
                if label_pv_or_area == "PV":
                    benefit_a = model.economical_benefit_a(add_power)
                elif label_pv_or_area == "area":
                    benefit_a = model.economical_benefit_a(power_pv)
                results.see_economical_benefit_a(benefit_a)  # type: ignore

        presence_overproduction_or_undeproduction(
            label_use_case,
            overproduction_or_undeproduction,
            results,
            consumption,
            region,
            percentage_daily_consumption,
        )


@validate_call
def presence_overproduction_or_undeproduction(
    label_use_case: common.LabelUseCaseType,
    overproduction_or_undeproduction: common.LabelOverproUnderprodType,
    results: Results,
    consumption: PositiveFloat,
    region: common.RegionType,
    percentage_daily_consumption: common.PercentageType,
):
    if overproduction_or_undeproduction == "Overproduction":
        results.see_CER_info(label_use_case)
    elif overproduction_or_undeproduction == "Underproduction":
        optimal_PV_size = model.optimal_sizing(
            consumption,
            region,
            percentage_daily_consumption,
        )
        results.see_optimal_size(optimal_PV_size)
