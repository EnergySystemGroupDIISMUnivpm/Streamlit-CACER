import datetime


def info_pv_or_area(user_input) -> tuple[int | None, datetime.date | None, int | None]:
    area = None
    year_pv = None
    power_pv = None
    has_pv_or_area = (
        user_input.pv_or_area()
    )  ##si potrebbe evitare di ripeterlo. Da rivedere.
    if has_pv_or_area == "Ho già un'area in cui costruirlo":
        area = user_input.insert_area()
    elif has_pv_or_area == "Ho già un impianto":
        year_pv, power_pv = user_input.insert_year_power_PV()

    return area, year_pv, power_pv
