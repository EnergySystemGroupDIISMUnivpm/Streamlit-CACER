from cProfile import label
import datetime

import streamlit as st
from pydantic import PositiveFloat, validate_call, BaseModel
import pandas as pd
import cacer_simulator.common as common
import plotly.graph_objects as go


def title_CACER():
    """
    title for the CACER simulator section.
    """
    st.markdown(" ")
    st.markdown("## Simulatore CACER")


class UserInput(BaseModel):

    ## Input in common for all 3 use case
    # Region
    def insert_region(self) -> common.RegionType | None:
        region: str | None = st.selectbox(
            "Seleziona la tua regione",
            common.REGIONS,
            index=None,
            placeholder="Seleziona un'opzione",
        )
        return region

    # Municipality
    def municipality(self) -> str | None:
        inhabitants: str | None = st.radio(
            "Il comune dove hai l'impianto fotovoltaico o dove vuoi costruirlo, ha meno di 5000 abitanti?",
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
            placeholder="Seleziona un'opzione",
        )

        if option is None:
            return None

        return consumption_options[option]

    # Power and year of PV
    @validate_call(validate_return=True)
    def insert_year_power_PV(
        self,
    ) -> tuple[datetime.date, PositiveFloat]:

        year_PV = st.date_input(
            "Inserisci la data di entrata in esercizio dell'impianto fotovoltaico",
            format="DD/MM/YYYY",
            key="PV_year",
        )
        power_PV = st.number_input(
            "Inserisci la potenza dell'impianto fotovoltaico in kW",
            step=0.1,
            format="%.1f",
            key="PV_power",
            min_value=round(common.POWER_PEAK / 1000, 1),
        )
        power_PV = common.round_data(power_PV)
        return year_PV, power_PV  # type: ignore

    def insert_area(self) -> int:
        area_PV: int | float = st.number_input(
            "Inserisci le dimensioni dell'area in m² in cui costruire l'impianto fotovoltaico",
            key="PV_area_dim",
            step=1,
            format="%d",
            min_value=round(common.AREA_ONE_PV),
        )
        return int(area_PV)

    def pv_or_area(self) -> str | None:
        has_pv_or_area: str | None = st.radio(
            "Hai già un impianto fotovoltaico o hai un area a disposizione in cui costruirlo?",
            options=["Ho già un impianto", "Ho un'area in cui costruirlo"],
            index=None,
            horizontal=True,
            key="pv_or_area",
        )
        return has_pv_or_area

    def boosting_power(self) -> int:
        added_power = st.number_input(
            "Di quanto vuoi potenziare il tuo impianto fotovoltaico in kW?",
            key="boosted_power",
            min_value=0,
            step=1,
            format="%d",
            help="Se non vuoi potenziare l'impianto fotovoltaico inserisci 0",
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

    # both for CER and Group
    def insert_members(
        self, label: str
    ) -> tuple[common.MembersWithValues, common.MembersWithValues]:
        charges_dict = common.MembersWithValues(
            bar=0, appartamenti=0, pmi=0, hotel=0, ristoranti=0
        )
        if label == "CER":
            col1, col2 = st.columns(2)
            with col1:
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
            with col2:
                st.markdown(
                    "Per ogni categoria, inserisci il numero di colonnine di ricarica, se presenti"
                )
                charges_dict = common.MembersWithValues(
                    bar=0, appartamenti=0, pmi=0, hotel=0, ristoranti=0
                )
                for member in charges_dict.keys():
                    number = st.number_input(
                        str(member),
                        min_value=0,
                        step=1,
                        key=f"chargers_member_{member}",
                    )
                    number = int(number)
                    charges_dict[member] = number

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
        return member_dict, charges_dict  # type: ignore

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
                f"""Abbiamo stimato che il tuo pannello produce circa {production} kWh in un anno."""
            )
        elif label == "area":
            st.write(
                f"""Abbiamo stimato che nell'area che hai inserito, l'impianto fotovoltaico che potresti costruirci produrrebbe circa {production} kWh in un anno"""
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
        benefit_b_pres = common.round_data(benefit_b_pres)
        st.markdown(
            f"Potresti ottenere fino a {benefit_b_pres}€ all'anno di incentivi economici.",
            help="Valori calcolati sulla base del decreto Decreto MASE n. 414 del 7 dicembre 2023 e del TIAD.",
        )

        if benefit_b_new is not None:
            benefit_b_new = common.round_data(benefit_b_new)
            st.markdown(
                f"Considerando anche i nuovi membri, potresti ricevere fino a {benefit_b_new}€ all'anno di incentivi economici.",
                help="Valori calcolati sulla base del decreto Decreto MASE n. 414 del 7 dicembre 2023 e del TIAD.",
            )

    def see_economical_benefit_a(self, benefit_a):
        benefit_a = common.round_data(benefit_a)

        st.write(
            f"Potresti ricevere fino a {benefit_a}€ a fondo perduto per la costruzione del tuo impianto fotovoltaico."
        )

    def see_environmental_benefit(
        self, environmental_benefit_pres, environmental_benefit_added=None
    ):
        environmental_benefit_pres = common.round_data(environmental_benefit_pres)
        st.markdown(
            f"""Abbiamo stimato che ridurresti le emissioni di circa {environmental_benefit_pres} kg CO2 ogni anno.""",
            help="Questi dati sono stati calcolati utilizzando il fattore di emissione medio riportato dall'Ispra per il 2022.",
        )

        if environmental_benefit_added is not None:
            environmental_benefit_added = common.round_data(environmental_benefit_added)
            st.markdown(
                f"Considerando anche i nuovi membri, abbiamo stimato che ridurresti le emissioni di circa {environmental_benefit_added} kg CO2 ogni anno.",
                help="Questi dati sono stati calcolati utilizzando il fattore di emissione medio riportato dall'Ispra per il 2022.",
            )

    def see_optimal_size(self, optim_size):
        optim_size = common.round_data(optim_size)

        st.markdown(
            f"In base ai tuoi consumi, la dimensione ottima del tuo impianto fotovoltaico sarebbe di circa {optim_size} kW. Valuta la possibilità di costruirlo.",
            help="Questi dati sono stati calcolati usando come riferimento le caratteristiche medie di un pannello fotovoltaico in silicio monocristallino.",
        )

    def see_installable_power(self, power_pv):
        power_pv = common.round_data(power_pv)

        st.markdown(
            f"""Nell'area che hai fornito potresti costruire un impianto fotovoltaico fino a {power_pv} kW.""",
            help="Questi dati sono stati calcolati usando come riferimento le caratteristiche medie di un pannello fotovoltaico in silicio monocristallino.",
        )

    def see_CER_info(self, label: str) -> None:
        if label == "Self_consumer":
            st.write(
                f"""Abbiamo stimato che in media produci più energia di quella di quella che consumi. Potresti condividere questa energia con altre persone.
                    Per esempio potresti valutare l'idea di partecipare a una Comunità Energetica Rinnovabile (CER).
                    Potresti ricevere ulteriori incentivi statali e miglioreresti il tuo impatto ambientale.
                    Per maggiori informazioni puoi provare la sezione CER di questo simulatore.
    """
            )
        elif label == "Group":
            st.write(
                f"""Abbiamo stimato che il tuo condominio produce più energia di quella che consuma. Potresti condividere l'energia in eccesso. 
                    Per esempio potresti valutare l'idea di far partecipare il tuo condominio a una Comunità Energetica Rinnovabile (CER).
                    Potresti ricevere ulteriori incentivi statali e miglioreresti il tuo impatto ambientale.
                    Per maggiori informazioni puoi provare la sezione CER di questo simulatore.
    """
            )

    @validate_call
    def see_computed_costs_plant(
        self,
        cost_plant: PositiveFloat,
        label_potenziamento_creazione: common.LabelCreationBoostingType,
    ):
        cost_plant = common.round_data(cost_plant)
        if label_potenziamento_creazione == "Potenziamento":
            st.write(
                f"Il costo del potenziamento del tuo impianto corrisponde circa a {cost_plant} €."
            )

        elif label_potenziamento_creazione == "Creazione":
            st.write(
                f"Il costo dell'installazione dell'impianto corrisponde circa a {cost_plant} €."
            )

    def see_optimal_area(self, optimal_area):
        optimal_area = common.round_data(optimal_area)
        st.markdown(
            f"""Per costruire l'impianto dalla potenza ottimale, avresti bisogno di circa {optimal_area} m².""",
            help="Questi dati sono stati calcolati usando come riferimento le caratteristiche medie di un pannello fotovoltaico in silicio monocristallino.",
        )

    def visualize_useful_information(self):
        st.markdown("##### **Informazioni sull'impianto fotovoltaico**")

    def visualize_economical_environmental_benefits(self):
        st.markdown("##### **Benefici economici e ambientali**")

    def visualize_advices(self):
        st.markdown("##### **Consigli**")

    def bar_chart_consum_prod(self, consumed_energy: float, produced_energy: float):
        energy_diff = produced_energy - consumed_energy
        df = pd.DataFrame(
            {
                "Energia Consumata nelle ore diurne (kWh)": [round(consumed_energy)],
                "Energia Rinnovabile Prodotta (kWh)": [round(produced_energy)],
                "Differenza (kWh)": [round(energy_diff)],
            }
        )

        [col1, col2] = st.columns(2)
        # Crea il grafico con Plotly
        st.markdown(" ")
        with col1:
            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=[
                        "Energia Consumata nelle ore diurne",
                        "Energia Rinnovabile Prodotta",
                        "Differenza tra Produzione e Consumo",
                    ],
                    y=[consumed_energy, produced_energy, energy_diff],
                    marker_color=["#0078AC", "#FFFF99", "#B9FDB9"],
                )
            )

            st.write(
                f"Confronto tra Energia Rinnovabile Consumata e Prodotta in un anno:"
            )
            fig.update_layout(
                yaxis_title="Energia (kWh)",
                yaxis_title_font_size=16,
                xaxis_title_font_size=16,
            )
            fig.update_traces(
                textfont_size=16,  # Imposta la dimensione del font
            )

            # Mostra il grafico in Streamlit
            st.plotly_chart(fig, key="bar_chart_consum_prod")
        with col2:
            # Mostra i valori in una tabella
            st.write(f"Valori dettagliati:")
            st.dataframe(df, hide_index=True, use_container_width=True)
