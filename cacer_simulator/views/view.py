from cProfile import label
import datetime

import streamlit as st
from pydantic import PositiveFloat, validate_call, BaseModel

import cacer_simulator.common as common


def title_CACER():
    st.markdown(" ")
    st.markdown("## Simulatore CACER")


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

    def insert_annual_consumption(self, label_use_case: str) -> int:
        if label_use_case == "Group":
            title = "Inserisci i consumi annui totali del tuo condominio in kWh"
        elif label_use_case == "CER":
            title = "Inserisci i consumi annui totali della tua CER in kWh"
        elif label_use_case == "Self_consumer":
            title = "Inserisci i tuoi consumi annui in kWh"
        annual_consumption = st.number_input(
            title,  # type:ignore
            key="consumption",
            step=1,
            format="%d",
            help="Inserisci il consumo annuo in kWh, puoi trovare i consumi annui all'interno delle bollette",
            min_value=1,
        )
        return int(annual_consumption)

    # Daytime percentage consumption
    def insert_percentage_daytime_consumption(self) -> float | None:
        consumption_options = {
            "più bassi": 0.25,
            "all'incirca uguali": 0.5,
            "più alti": 0.75,
        }
        option = st.selectbox(
            "In una giornata tipo, come sono i consumi diurni rispetto ai consumi notturni?",
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
            step=0.1,
            format="%.1f",
            key="PV_power",
            min_value=1.1,
        )

        return year_PV, int(power_PV)  # type: ignore

    def insert_area(self) -> int:
        area_PV: int | float = st.number_input(
            "Inserisci le dimensioni dell'area in m² in cui costruire l'impianto",
            key="PV_area_dim",
            step=1,
            format="%d",
            min_value=round(common.AREA_ONE_PV) * 3,
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

    def insert_members(self, label: str) -> common.MembersWithValues:
        if label == "CER":
            st.markdown(
                "Inserisci il numero di membri della tua CER per ogni categoria"
            )
            member_dict = common.MembersWithValues(
                bar=0, appartamenti=0, pmi=0, hotel=0, ristoranti=0
            )
            for member in member_dict.keys():
                number = st.number_input(
                    str(member), min_value=0, step=1, key=f"cer_member_{member}"
                )
                number = int(number)
                member_dict[member] = number
        elif label == "Group":
            appartments = st.number_input(
                "Inserisci il numero di appartamenti presenti nel tuo condominio",
                min_value=0,
                step=1,
                key="appartments",
            )
            appartments = int(appartments)
            member_dict = common.MembersWithValues(
                bar=0, appartamenti=appartments, pmi=0, hotel=0, ristoranti=0
            )
        return member_dict  # type: ignore

    def know_members_consumption(self, label: str) -> str | None:
        if label == "CER":
            stringa = "dei membri della tua CER"
        elif label == "Group":
            stringa = "del tuo condominio"
        members_consumption: str | None = st.radio(
            f"Conosci i consumi energetici {stringa}?",  # type: ignore
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="members_consumption",
        )
        return members_consumption


class Results(BaseModel):

    def see_results(self) -> bool:
        view_result = st.button(
            "Clicca qui per vedere i risultati", key="visualize-result"
        )

        return view_result

    def see_production(self, production: PositiveFloat, label: str):
        production = round(production)
        if label == "PV":
            st.write(
                f"""Abbiamo stimato che il tuo pannello produce circa {production} kWh in un anno"""
            )
        elif label == "area":
            st.write(
                f"""Abbiamo stimato che con l'area che hai inserito l'impianto che potresti costruirci produrrebbe circa {production} kWh in un anno"""
            )

    def see_optimal_members(
        self, optimal_members: common.MembersWithValues, label: str
    ):
        messages = {
            "membri non presenti": "I membri ideali con cui potresti costituire la CER per ottimizzare l'energia autoconsumata sono:",
            "membri già presenti": "Ai membri della tua CER, potresti aggiungere i seguenti membri per ottimizzare l'energia autoconsumata :",
        }

        message = messages.get(label, None)
        filtered_data = {k: v for k, v in optimal_members.items() if v > 0}  # type: ignore
        result_list = [f"{v} {k}" for k, v in filtered_data.items()]
        result_string = ", ".join(result_list)
        if message:
            st.write(f"{message} {result_string}")
        else:
            st.write("Label non riconosciuto.")

    def see_economical_benefit_b(self, benefit_b_pres, benefit_b_new=None):
        benefit_b_pres = round(benefit_b_pres)
        st.write(
            f"Abbiamo calcolato che i tuoi incentivi economici di tipo B corrispondono a {benefit_b_pres}€ all'anno."
        )

        if benefit_b_new is not None:
            benefit_b_new = round(benefit_b_new)
            st.write(
                f"Abbiamo calcolato che i tuoi incentivi economici di tipo B considerando anche i nuovi membri corrispondono a {benefit_b_new}€ all'anno."
            )

    def see_economical_benefit_a(self, benefit_a):
        benefit_a = round(benefit_a)

        st.write(
            f"Abbiamo calcolato che i tuoi incentivi economici di tipo A corrispondono a {benefit_a}€."
        )

    def see_environmental_benefit(
        self, environmental_benefit_pres, environmental_benefit_added=None
    ):
        environmental_benefit_pres = round(environmental_benefit_pres)
        st.write(
            f"Abbiamo calcolato che ridurresti le emissioni di {environmental_benefit_pres} kg CO2 ogni anno."
        )

        if environmental_benefit_added is not None:
            environmental_benefit_added = round(environmental_benefit_added)
            st.write(
                f"Abbiamo calcolato che ridurresti le emissioni, considerando i nuovi membri, di {environmental_benefit_added} kg CO2 ogni anno."
            )

    def see_optimal_size(self, optim_size):
        optim_size = round(optim_size)

        st.write(
            f"Abbiamo calcolato che il dimensionamento ottimo del tuo impianto in base a i tuoi consumi corrisponde a {optim_size} Kw."
        )

    def see_installable_power(self, power_pv):
        power_pv = round(power_pv)

        st.write(
            f"Abbiamo calcolato che con l'area che hai fornito potresti costruire un impianto fino a {power_pv} Kw."
        )

    def see_CER_info(self, label: str) -> None:
        if label == "Self_consumer":
            st.write(
                f"""Abbiamo stimato che in media produci più energia di quella di quella che consumi. Potresti condividere questa energia con altre persone.
                    Per esempio potresti valutare l'idea di partecipare a una Comunità Energetica Rinnovabile (CER).
                    Potresti ricevere ulteriori incetivi statali e migliorersti il tuo impatto ambientale.
                    Per maggiori informazioni puoi provare la sezione CER di questo simulatore.
    """
            )
        elif label == "Group":
            st.write(
                f"""Abbiamo stimato che il tuo condominio produce più energia di quella che consuma. Potresti condividere l'energia in eccesso. 
                    Per esempio potresti valutare l'idea di far partecipare il tuo condominio a una Comunità Energetica Rinnovabile (CER).
                    Potresti ricevere ulteriori incetivi statali e migliorersti il tuo impatto ambientale.
                    Per maggiori informazioni puoi provare la sezione CER di questo simulatore.
    """
            )

    def see_computed_costs_plant(
        self, cost_plant: PositiveFloat, label_potenziamento_creazione: str
    ):
        cost_plant = round(cost_plant)
        if label_potenziamento_creazione == "Potenziamento":
            st.write(
                f"Il costo del potenziamento del tuo impianto corrisponde circa a {cost_plant} €."
            )

        elif label_potenziamento_creazione == "Creazione":
            st.write(
                f"Il costo dell'installazione dell'impianto corrisponde circa a {cost_plant} €."
            )

    def visualize_useful_information(self):
        st.markdown("##### **Informazioni sull'impianto**")

    def visualize_economical_environmental_benefits(self):
        st.markdown("##### **Benefici economici e ambientali**")

    def visualize_advices(self):
        st.markdown("##### **Consigli**")
