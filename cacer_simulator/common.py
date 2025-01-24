from enum import StrEnum
from typing import Annotated, NotRequired

from pydantic import AfterValidator, BaseModel, Field
from typing_extensions import TypedDict
import random

REGIONS = [
    "Abruzzo",
    "Basilicata",
    "Calabria",
    "Campania",
    "Emilia-Romagna",
    "Friuli-Venezia Giulia",
    "Lazio",
    "Liguria",
    "Lombardia",
    "Marche",
    "Molise",
    "Piemonte",
    "Puglia",
    "Sardegna",
    "Sicilia",
    "Trentino-Alto Adige",
    "Toscana",
    "Umbria",
    "Valle d'Aosta",
    "Veneto",
]


def is_valid_region(x: str) -> str:
    if x not in REGIONS:
        raise ValueError(f"Invalid Region {x}, must be in {REGIONS}")
    return x


RegionType = Annotated[
    str,
    AfterValidator(is_valid_region),
    Field(description=f"Region among {REGIONS}"),
]

LABEL_USE_CASE = ["CER", "Group", "Self_consumer"]


def is_valid_use_case(x: str) -> str:
    if x not in LABEL_USE_CASE:
        raise ValueError(f"Invalid Lable use case {x}, must be in {LABEL_USE_CASE}")
    return x


LabelUseCaseType = Annotated[
    str,
    AfterValidator(is_valid_use_case),
    Field(description=f"Label use case among {LABEL_USE_CASE}"),
]

LABEL_PV_AREA = ["PV", "area"]


def is_valid_label_pv_area(x: str) -> str:
    if x not in LABEL_PV_AREA:
        raise ValueError(
            f"Invalid Lable for pv or area {x}, must be in {LABEL_PV_AREA}"
        )
    return x


LabelPVAreaType = Annotated[
    str,
    AfterValidator(is_valid_label_pv_area),
    Field(description=f"Label use case among {LABEL_PV_AREA}"),
]

LABEL_CREATION_BOOSTING = ["Creazione", "Potenziamento"]


def is_valid_creation_boosting_label(x: str) -> str:
    if x not in LABEL_CREATION_BOOSTING:
        raise ValueError(
            f"Invalid Lable for creation or boosting {x}, must be in {LABEL_CREATION_BOOSTING}"
        )
    return x


LabelCreationBoostingType = Annotated[
    str,
    AfterValidator(is_valid_creation_boosting_label),
    Field(description=f"Label use case among {LABEL_CREATION_BOOSTING}"),
]

LABEL_OVER_UNDER = ["Overproduction", "Underproduction", "Optimal"]


def is_valid_label_over_under(x: str) -> str:
    if x not in LABEL_OVER_UNDER:
        raise ValueError(
            f"Invalid Lable for overproduction or underproduction {x}, must be in {LABEL_OVER_UNDER}"
        )
    return x


LabelOverproUnderprodType = Annotated[
    str,
    AfterValidator(is_valid_label_over_under),
    Field(
        description=f"Label Overproduction or Underproduction among {LABEL_OVER_UNDER}"
    ),
]

PercentageType = Annotated[
    float,
    Field(ge=0, le=1, description="Percentage value"),
]

PositiveOrZeroFloat = Annotated[
    float,
    Field(ge=0, description="Positive or zero value"),
]


# mean values of irradiance for each region (kW/m2)
_irradiance_values = [
    1575,  # Abruzzo
    1603,  # Basilicata
    1677,  # Calabria
    1611,  # Campania
    1477,  # Emilia-Romagna
    1365,  # Friuli-Venezia Giulia
    1632,  # Lazio
    1500,  # Liguria
    1433,  # Lombardia
    1504,  # Marche
    1568,  # Molise
    1454,  # Piemonte
    1633,  # Puglia
    1714,  # Sardegna
    1786,  # Sicilia
    1390,  # Trentino-Alto Adige
    1548,  # Toscana
    1541,  # Umbria
    1502,  # Valle d'Aosta
    1424,  # Veneto
]

# mean values of production for Kw for each region based on Nord, South, Centre
regional_production = [
    1400,  # Abruzzo
    1400,  # Basilicata
    1400,  # Calabria
    1400,  # Campania
    1100,  # Emilia-Romagna
    1100,  # Friuli-Venezia Giulia
    1250,  # Lazio
    1100,  # Liguria
    1100,  # Lombardia
    1250,  # Marche
    1400,  # Molise
    1100,  # Piemonte
    1400,  # Puglia
    1400,  # Sardegna
    1400,  # Sicilia
    1100,  # Trentino-Alto Adige
    1250,  # Toscana
    1250,  # Umbria
    1100,  # Valle d'Aosta
    1100,  # Veneto
]
# dictionary with the irradiance values
IRRADIANCE: dict = dict(zip(REGIONS, _irradiance_values))

# dictionary with the production values
PRODUCTION: dict = dict(zip(REGIONS, regional_production))

# average loss factor to take into account losses in the system, such as those due to the inverter, wiring, dust on the panels ecc.
LOSS_FACTOR: float = 0.8

# efficiency of an average PV
EFFICIENCY: float = 0.2

# power of one singular PV pannel in W
POWER_PEAK = 300

# area of 1 single pannel in m2 with the power defined as power peak
AREA_ONE_PV = 1.7 * 1.1

kw_cost: dict[tuple[float, float], int] = {
    (0, 5): 1500,
    (5, 10): 1300,
    (10, 50): 1200,
    (50, float("inf")): 1000,
}


def get_kw_cost(plant_power: int | float) -> int:

    if plant_power <= 0:
        return 0
    else:
        for power_range, cost in kw_cost.items():
            if power_range[0] <= plant_power < power_range[1]:
                return cost
    return 0


# how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
AVG_EMISSIONS_FACTOR = 0.309

# INCENTIVES
ARERA_VALORISATION = 10  # valorisation of ARERA


class Tariff(BaseModel):

    # Tariff definitions acconrding to implant power
    tariff_dict: dict[tuple[int, int], int] = {
        (0, 200): 120,  # implant power < 200, incetive is maximum 120 euro/MWh
        (200, 600): 110,
        (600, 1000): 100,
    }

    # tariff depending on ihabitants
    tariff_municipality_dict: dict[tuple[int, int] | tuple[int, float], int] = {
        (0, 20): 1500,  # implant <20kWp incentive=1500euro for kW
        (20, 200): 1200,
        (200, 600): 1100,
        (600, float("inf")): 1050,
    }

    def get_tariff(self, plant_power: int | float) -> int:

        assert plant_power >= 0, "plant power must be positive to compute tariff!"

        for power_range, tariff in self.tariff_dict.items():
            if power_range[0] <= plant_power < power_range[1]:
                return tariff
        return 0

    def get_tariff_municipality(self, plant_power: int | float) -> int:

        assert plant_power >= 0, "plant power must be positive to compute tariff!"

        for power_range, tariff in self.tariff_municipality_dict.items():
            if power_range[0] <= plant_power < power_range[1]:
                return tariff
        return 0


# tariff increase basing on Region
REGIONAL_TARIFF_INCREASE = {
    "Lazio": 4,
    "Marche": 4,
    "Toscana": 4,
    "Umbria": 4,
    "Abruzzo": 4,
    "Emilia-Romagna": 10,
    "Friuli-Venezia Giulia": 10,
    "Liguria": 10,
    "Lombardia": 10,
    "Piemonte": 10,
    "Veneto": 10,
    "Trentino-Alto Adige": 10,
    "Valle d'Aosta": 10,
}


MEMBERS = [
    "bar",
    "appartamenti",
    "pmi",
    "hotel",
    "ristoranti",
]


class OptionalMembersWithValues(TypedDict):
    bar: NotRequired[int]
    appartamenti: NotRequired[int]
    pmi: NotRequired[int]
    hotel: NotRequired[int]
    ristoranti: NotRequired[int]


class MembersWithValues(TypedDict):
    bar: int
    appartamenti: int
    pmi: int
    hotel: int
    ristoranti: int


class ConsumptionByMember(BaseModel):

    CONSUMPTION_RATES_DIURNAL_HOURS: MembersWithValues = {
        "bar": 15400,
        "appartamenti": 600,
        "pmi": 20000,
        "hotel": 280000,
        "ristoranti": 15000,
    }

    # avg annual consumptions in kWh
    CONSUMPTION_RATES: MembersWithValues = {
        "bar": 22000,
        "appartamenti": 2000,
        "pmi": 25000,
        "hotel": 700000,
        "ristoranti": 30000,
    }
    CONSUMPTION_RATES_CHARGING_STATION: MembersWithValues = {
        "bar": 46 * 24,
        "appartamenti": 3
        * 8
        * 146,  # 24kWh (considering charging stations of 3kW used for 8hours) each 2.5 days
        "pmi": 22
        * 8
        * 300,  # (charging statitions of 22kW used for 8hours for 300days)
        "hotel": 22 * 8 * 300,
        "ristoranti": 22 * 4 * 300,
    }  # TODO:aggiornali sulla base di valori reali

    CONSUMPTION_PERCENTAGE: MembersWithValues = {
        "bar": 70,
        "appartamenti": 30,
        "pmi": 80,
        "hotel": 40,
        "ristoranti": 50,
    }

    @property
    def members(self) -> list[str]:
        return MEMBERS

    def get_consump_random(self) -> list[tuple[str, int]]:
        return sorted(  # type: ignore
            self.CONSUMPTION_RATES_DIURNAL_HOURS.items(),
            key=lambda _: random.random(),  # type: ignore
        )

    def get_sorted_diurnal(self, reverse: bool = False) -> list[tuple[str, int]]:
        return sorted(  # type: ignore
            self.CONSUMPTION_RATES_DIURNAL_HOURS.items(),
            key=lambda x: x[1],  # type: ignore
            reverse=reverse,
        )

    def get_sorted(self, reverse: bool = False) -> list[tuple[str, int]]:
        return sorted(  # type: ignore
            self.CONSUMPTION_RATES.items(),
            key=lambda x: x[1],  # type: ignore
            reverse=reverse,
        )

    def get_consumption_value(self, member: str, diurnal: bool = False) -> int:
        if diurnal:
            return self.CONSUMPTION_RATES_DIURNAL_HOURS.get(member, 0)
        return self.CONSUMPTION_RATES.get(member, 0)

    def get_consumption_charging_station_value(self, member: str) -> int:
        return self.CONSUMPTION_RATES_CHARGING_STATION.get(member, 0)

    def get_consumption_percentage(self, member: str) -> int:
        return self.CONSUMPTION_PERCENTAGE.get(member, 0)


def round_data(data: float | int):
    if data >= 1:
        data = round(data)
    else:
        data = round(data, 1)
    return data
