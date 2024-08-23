import datetime

import streamlit as st
from pydantic import PositiveFloat, validate_call, BaseModel

import cacer_simulator.common as common


class UserInput(BaseModel):

    ## Input in common for all 3 use case
    # Region
    def insert_region(self) -> common.RegionType | None:
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
    @validate_call(validate_return=True)
    def insert_year_power_PV(
        self,
    ) -> tuple[datetime.date, int]:

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

        return year_PV, int(power_PV)  # type: ignore

    def insert_area(self) -> int:
        area_PV: int | float = st.number_input(
            "Inserisci le dimensioni dell'area in m² in cui costruire l'impianto",
            key="PV_area_dim",
            step=1,
            format="%d",
        )
        return int(area_PV)

    def pv_or_area(self) -> str | None:
        has_pv_or_area: str | None = st.radio(
            "Hai già un impianto PV o hai un area a disposizione in cui costruirlo?",
            options=["Ho già un impianto", "Ho un'area in cui costruirlo"],
            index=None,
            horizontal=True,
            key="pv_or_area",
        )
        return has_pv_or_area

    def boosting_power(self) -> int:
        added_power = st.number_input(
            "Di quanto vuoi potenziare il tuo impianto in kW?",
            key="boosted_power",
            min_value=0,
            step=1,
            format="%d",
            help="Se non vuoi potenziare l'impianto inserisci 0",
        )
        return int(added_power)

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

    def insert_members(self) -> common.MembersWithValues:
        st.markdown("Inserisci il numero di membri della tua CER per ogni categoria")
        member_dict = common.MembersWithValues(
            bar=0, appartamenti=0, pmi=0, hotel=0, ristoranti=0
        )
        for member in member_dict.keys():
            number = st.number_input(
                str(member), min_value=0, step=1, key=f"cer_member_{member}"
            )
            number = int(number)
            member_dict[member] = number
        return member_dict

    def know_members_consumption(self) -> str | None:
        members_consumption: str | None = st.radio(
            "Conosci i consumi energetici dei membri della tua CER?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="cer_members_consumption",
        )
        return members_consumption


class Results(BaseModel):

    def see_results(self) -> bool:
        view_result = st.button(
            "Clicca qui per vedere i risultati", key="visualize-result"
        )

        return view_result

    def see_production(self, production: PositiveFloat):
        production = round(production)
        st.write(
            f"""Abbiamo stimato che il tuo pannello produce circa {production} kWh in un anno"""
        )

    def see_optimal_members(
        self, optimal_members: common.MembersWithValues, label: str
    ):
        messages = {
            "membri non presenti": "I membri ideali con cui potresti costituire la CER per ottimizzare l'energia autoconsumata e gli incentivi sono:",
            "membri già presenti": "Ai membri della tua CER, potresti aggiungere i seguenti membri per ottimizzare l'energia autoconsumata e gli incentivi:",
        }

        message = messages.get(label, None)

        if message:
            st.write(f"{message} {optimal_members}")
        else:
            st.write("Label non riconosciuto.")
