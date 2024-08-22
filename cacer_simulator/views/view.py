import datetime
from typing import Never, Tuple

import streamlit as st

import cacer_simulator.common as common


class UserInput:

    ## Input in common for all 3 use case
    # Region
    def insert_region(self) -> str | None:
        region: str | None = st.selectbox(
            "Seleziona la tua regione", common.REGIONS, index=None
        )
        return region

    # Municipality
    def municipality(self) -> str | None:
        inhabitants: str | None = st.radio(
            "Il comune dove hai l'impianto o dove vuoi costruirlo, ha meno di 5000 abitanti?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="comune_inhabitants",
        )
        return inhabitants

    # Annual consumption  ----'label' da implemntare nel controller.py ??????

    def insert_annual_consumption(self, label: str) -> int:
        annual_consumption = st.number_input(
            label,
            key="consumption",
            step=1,
            format="%d",
            help="Inserisci il consumo annuo in kWh, puoi trovare i consumi annui all'interno delle bollette",
        )
        return int(annual_consumption)

    # Daytime percentage consumption
    def insert_percentage_daytime_consumption(self) -> float | None:
        consumption_options = {"poco": 0.25, "non c'è differenza": 0.5, "molto": 0.75}
        option = st.selectbox(
            "In una giornata tipo quanto diresti che i consumi sono più alti di giorno piuttosto che di notte?",
            options=list(consumption_options.keys()),
            index=None,
            key="daytime_consump",
        )

        if option is None:
            return None

        return consumption_options[option]

    # Power and year of PV
    def insert_year_power_PV(
        self,
    ) -> Tuple[
        datetime.date
        | Tuple[Never]
        | Tuple[datetime.date]
        | Tuple[datetime.date]
        | None
        | int
    ]:  ### tipizzazione tupla???
        year_PV = st.date_input(
            "Inserisci la data di entrata in esercizio dell'impianto PV",
            format="DD/MM/YYYY",
            key="PV_year",
        )
        power_PV = st.number_input(
            "Inserisci la potenza dell'impianto PV in kW",
            step=1,
            format="%d",
            key="PV_power",
        )
        return year_PV, int(power_PV)

    def insert_area(self) -> int:
        area_PV: int | float = st.number_input(
            "Inserisci le dimensioni dell'area in m² in cui costruire l'impianto",
            key="PV_area_dim",
            step=1,
            format="%d",
        )
        return area_PV

    ## Input for only CER
    # Knowing with making the cer
    def cer_with(self) -> str | None:
        members_info: str | None = st.radio(
            "Sai già con chi fare la CER?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="cer_members_info",
        )
        return members_info
