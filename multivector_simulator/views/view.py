import streamlit as st
from pydantic import BaseModel, validate_call
import pandas as pd
import numpy as np
from traitlets import default
import multivector_simulator.common as common
from pydantic import PositiveFloat, validate_call, PositiveInt, NonNegativeInt
from enum import StrEnum


def title_multivettore():
    st.markdown(" ")
    st.markdown("## Simulatore Multivettore Energetico")


def read_excel_file(file_path):
    with open(file_path, "rb") as file:
        return file.read()


# Input


class KnwonProfileConsump_or_Total(StrEnum):
    KnwonProfileConsump = "Si"
    KnwonTotalConsump = "No"


class UserInput(BaseModel):
    def select_profileConsump_or_onlyTotal(self) -> KnwonProfileConsump_or_Total | None:
        profileConsump_or_onlyTotal = st.radio(
            """Conosci i tuoi consumi elettrici (kWh),caloriferi (kWh termici) e frigoriferi (kWh termici) orari riferiti ad un periodo di un anno intero?""",
            options=[
                KnwonProfileConsump_or_Total.KnwonProfileConsump,
                KnwonProfileConsump_or_Total.KnwonTotalConsump,
            ],
            key="profileConsump_or_onlyTotal",
            index=None,
        )
        if profileConsump_or_onlyTotal is None:
            return None
        return KnwonProfileConsump_or_Total(profileConsump_or_onlyTotal)

    @validate_call
    def download_upload_consumption(self) -> common.ConsumptionDataFrameType | None:
        """
        Function that gives the possibility to user to download an excel file, complete it and upload it with its Electrical, Thermal and Refrigerator compsumptions.
        """
        df_uploaded = None
        st.markdown("  ")
        st.markdown(
            """Scarica, compila con i tuoi consumi energetici e ricarica il file excel. Il file deve contenere i consumi elettrici (kWh), caloriferi (kWh termici) e frigoriferi (kWh termici) orari riferiti ad un periodo di un anno intero (8760 ore).  \n Se inserisci consumi frigoriferi diversi da zero, il simulatore prenderà in considerazione la possibilità di installare un impianto PV, una batteria, una pompa di calore reversibile e un impianto di trigenerazione.  \n Se inserisci consumi frigoriferi nulli, il simulatore prenderà in considerazione la possibilità di installare un impianto PV, una batteria, una pompa di calore reversibile e un impianto di cogenerazione."""
        )
        file_path = "./resources/Esempio_input_consumi_multienergetico.xlsx"
        if st.download_button(
            label="Scarica il file excel",
            data=read_excel_file(file_path),
            file_name="Esempio_input_consumi_multienergetico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ):
            st.success("File scaricato! Controlla tra i tuoi download.")
        uploaded_file = st.file_uploader(
            "Carica il file excel compilato", type=["xlsx"]
        )

        if uploaded_file is not None:
            df_uploaded = pd.read_excel(uploaded_file, engine="openpyxl")

            try:
                # validation of the file. Check that it complies with our model
                df_uploaded = common.validate_consumption_dataframe(df_uploaded)
                st.success("Contenuto del file Excel caricato con successo:")
                st.dataframe(df_uploaded)
            except ValueError as e:
                st.error(f"Errore di validazione: {e}")
                return None
            return df_uploaded

        return None

    def unknown_consumption_profile(self):
        st.markdown(" ")
        st.markdown("##### Non hai a disposizione i consumi orari?")
        unknown_profiles = st.button(label="Inserisci solo i consumi totali annui")
        return unknown_profiles

    def insert_annual_consumption(self) -> tuple[int | None, int | None, int | None]:
        """
        Insert total annual consumption.
        """
        st.markdown(" ")
        st.markdown(
            "##### Non conosci i consumi orari? Inserisci solo i consumi totali annui qui sotto"
        )
        with st.form(key="input_form", border=False):
            electric = st.number_input("Inserisci i consumi elettrici in kWh", step=1)
            thermal = st.number_input(
                "Inserisci i consumi termici in kWh termici", step=1
            )
            refrig = st.number_input(
                "Inserisci i consumi frigoriferi in kWh termici", step=1
            )
            submit_button = st.form_submit_button(label="Carica i dati")
            if submit_button:
                st.success(
                    "Dati caricati con successo! Premi il pulsante qui sotto per visualizzare i risultati della simulazione."
                )
                return int(electric), int(thermal), int(refrig)
            else:
                return None, None, None

    def select_period_plot(self):
        st.markdown(" ")
        st.markdown(
            "###### **Qui sotto puoi visulaizzare l'andamento tipico dell'energia che consumi e che produrresti con gli impianti consigliati**",
            help="Per andamento tipico si intende l'andamento medio calcolato sui dati annuali",
        )
        period_label = None
        period_label = st.radio(
            "Per prima cosa, seleziona la durata del periodo in cui vuoi visualizzare l'andamento della tua energia",
            options=list(common.PERIOD_TO_BE_PLOTTED.keys()),
            index=0,
            key="select label of period",
        )
        return period_label


# Output
class UserOuput(BaseModel):
    def no_result_found(self):
        st.markdown(
            """La simulazione non ha prodotto una soluzione ottimale questa volta. Ricarica la pagina e prova ad effettuare nuovamente la simulazione: potrebbe esplorare nuove possibilità e trovare un risultato."""
        )

    def see_results(self) -> bool:
        """
        Botton to visualize results
        """
        view_result = st.button(
            "Clicca qui per vedere la tipologia e la dimensione ottimale degli impianti che potresti installare in base ai tuoi consumi",
            key="visualize-result-multivettore",
            help="Questi valori sono stati calcolati attraverso un metodo di ottimizzazione basato sul gradiente con lo scopo di minimizzare i costi (in un periodo di 20 anni) e di massimizzare la copertura dei consumi.",
        )

        return view_result

    def see_optimal_sizes(
        self,
        pv_size: NonNegativeInt,
        cogen_size: NonNegativeInt,
        trigen_size: NonNegativeInt,
        battery_size: NonNegativeInt,
    ):
        st.markdown("##### **Risulati del simulatore**")
        st.markdown(
            """Per massimizzare la copertura dei tuoi consumi e minimizzare i costi puoi installare i seguenti impianti:
"""
        )
        if pv_size > 0:
            self.see_pv_size(pv_size)
        if cogen_size > 0:
            self.see_cogen_size(cogen_size)
        if trigen_size > 0:
            self.see_trigen_size(trigen_size)
        if battery_size > 0:
            self.see_battery_size(battery_size)

    def see_pv_size(self, pv_size: NonNegativeInt):
        st.markdown(f"- un **impianto fotovoltaico** da {pv_size} kW")

    def see_cogen_size(self, cogen_size: NonNegativeInt):
        st.markdown(
            f"- un **impianto di cogenerazione** da {cogen_size} kW",
            help=common.Trigen_Cogen().info_biomass,
        )

    def see_trigen_size(self, trigen_size: NonNegativeInt):
        st.markdown(
            f"- un **impianto di trigenerazione** da {trigen_size} kW",
            help=common.Trigen_Cogen().info_biomass,
        )

    def see_battery_size(self, battery_size: NonNegativeInt):
        st.markdown(f"- un **impianto di accumulo** da {battery_size} kWh")

    def see_costs_investment_recovery(
        self, costs: PositiveFloat, recovery_time: PositiveInt | float
    ):
        trigen_cogen = common.Trigen_Cogen()
        if recovery_time > 0 and recovery_time < 21:
            st.markdown(
                f"Il costo previsto per l'installazione degli impianti è di circa {costs}€. Grazie all'energia autoprodotta, riusciresti a recuperare l'investimento in circa {recovery_time} anni.",
                help=f"Il tempo di recupero è stato calcolato tenendo conto di un prezzo dell'energia elettrica da rete pari a {common.ELECTRIC_ENERGY_PRICE}€/kWh, un costo dell'energia termica da rete pari a {common.THERMAL_ENERGY_PRICE}€/kWh e un costo del carburante per il cogeneratore pari a {trigen_cogen.COST_GAS_FOR_GEN}€/Smc.",
            )
        elif recovery_time < 0:
            st.markdown(
                f"Il costo previsto per l'installazione degli impianti è di circa {costs}€. Grazie all'energia autoprodotta, riusciresti a recuperare l'investimento in meno di un anno.",
                help=f"Il tempo di recupero è stato calcolato tenendo conto di un prezzo dell'energia elettrica da rete pari a {common.ELECTRIC_ENERGY_PRICE}€/kWh, un costo dell'energia termica da rete pari a {common.THERMAL_ENERGY_PRICE}€/kWh e un costo del carburante per il cogeneratore pari a {trigen_cogen.COST_GAS_FOR_GEN}€/Smc.",
            )
        else:
            st.markdown(
                f"Il costo previsto per l'installazione degli impianti è di circa {costs}€."
            )

    def see_environmental_benefit(self, reduced_CO2: PositiveFloat):
        st.markdown(
            f"Attraverso l'uso e l'installazione di questi impianti ridurresti le emissioni di circa {reduced_CO2} kg CO2 ogni anno.",
            help="Questi dati sono stati calcolati utilizzando il fattore di emissione medio riportato dall'Ispra per il 2022.",
        )

    ##GRAPH PRODUCTION AND CONSUMPTION
    @validate_call()
    def extract_period_from_period_label(
        self, period_label: common.LabelPeriodLabelsList
    ) -> int:
        period = common.PERIOD_TO_BE_PLOTTED[period_label]
        return period

    def see_coverage_energy_plot(
        self,
        consumed_energy: np.ndarray,
        produced_energy: np.ndarray,
        energy_type: common.LabelEnergyType,
        period_label: str,
    ):
        """
        Plot graph showing the trend of energy consumed and produced over a period of time (hours)
        """
        ore = np.arange(len(consumed_energy))
        chart_data = pd.DataFrame(
            {
                "Ore": ore,
                f"Consumata": consumed_energy,
                f"Prodotta": produced_energy,
            }
        )
        st.markdown(
            f"""Distribuzione media {period_label} dell'Energia {energy_type} prodotta e consumata"""
        )
        st.area_chart(chart_data, x="Ore", y_label="kWh", x_label="Ore")

    def graph_return_investment(
        self,
        df_cumulative_costs_and_savings: pd.DataFrame,
    ):
        st.markdown(
            "##### **Andamento Cumulativo di Costi e Risparmi Annuali**",
            help="Questo grafico mostra l'andamento cumulativo di costi e risparmi annuali, partendo dal costo iniziale dell'installazione  degli impianti e includendo i costi e i risparmi accumulati ogni anno. I valori negativi rappresentano le spese, mentre i valori positivi indicano i risparmi ottenuti. Il punto in cui la barra cumulativa supera lo zero rappresenta il momento in cui si ottiene il ritorno dell'investimento, segnando il passaggio da una situazione di costo netto a una di guadagno.",
        )
        years = common.Optimizer().YEARS
        st.bar_chart(
            df_cumulative_costs_and_savings.set_index("Year")["Cumulative value"],
            x_label="Anni dopo l'installazione degli impianti",
            y_label="€",
        )
