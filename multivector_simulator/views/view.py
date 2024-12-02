import streamlit as st
from pydantic import BaseModel, validate_call
import pandas as pd
import numpy as np
import multivector_simulator.common as common
from pydantic import PositiveFloat, validate_call, PositiveInt, NonNegativeInt


def title_multivettore():
    st.markdown(" ")
    st.markdown("## Simulatore Multivettore Energetico")


def read_excel_file(file_path):
    with open(file_path, "rb") as file:
        return file.read()


# Input


class UserInput(BaseModel):

    @validate_call
    def download_upload_consumption(self) -> common.ConsumptionDataFrameType | None:
        """
        Function that gives the possibility to user to download an excel file, complete it and upload it with its Electrical, Thermal and Refrigerator compsumptions.
        """
        df_uploaded = None
        st.markdown("  ")
        st.markdown(
            """Scarica, Compila con i tuoi consumi energetici e Ricarica il File Excel. Il file deve contenere i consumi elettrici, caloriferi e frigoriferi orari riferiti ad un periodo di un anno.  \n Se inserisci consumi frigoriferi diversi da zero, il simulatore prenderà in considerazione la possibilità di installare un impianto PV, una batteria e un impianto di trigenerazione.  \n Se inserisci consumi frigoriferi nulli, il simulatore prenderà in considerazione la possibilità di installare un impianto PV, una batteria e un impianto di cogenerazione."""
        )
        file_path = "./resources/Esempio_input_consumi_multienergetico.xlsx"
        st.download_button(
            label="Scarica il file Excel",
            data=read_excel_file(file_path),
            file_name="Esempio_input_consumi_multienergetico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        uploaded_file = st.file_uploader(
            "Carica il file Excel compilato", type=["xlsx"]
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

    def insert_winter_season(self) -> tuple[PositiveInt, PositiveInt]:
        """
        Function that gives the possibility to user to insert the start and the end of the winter season.
        Returns the start and the end months of the winter season in integers (0=January)
        """
        st.markdown("Quando inizia la stagione invernale?")
        mese_to_num = {
            "Gennaio": 0,
            "Febbraio": 1,
            "Marzo": 2,
            "Aprile": 3,
            "Maggio": 4,
            "Giugno": 5,
            "Luglio": 6,
            "Agosto": 7,
            "Settembre": 8,
            "Ottobre": 9,
            "Novembre": 10,
            "Dicembre": 11,
        }

        # Ottieni i valori dai selectbox di Streamlit
        start_winter_season = st.selectbox(
            "Inserisci il mese di inizio della stagione invernale",
            options=list(mese_to_num.keys()),
            index=10,
            key="inizio_stag_invernale",
            label_visibility="visible",
        )

        end_winter_season = st.selectbox(
            "Inserisci il mese di fine della stagione invernale",
            options=list(mese_to_num.keys()),
            index=3,
            key="fine_stag_invernale",
            label_visibility="visible",
        )

        mesi = list(mese_to_num.keys())
        return mesi.index(start_winter_season), mesi.index(end_winter_season)

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
            index=None,
            key="select label of period",
        )
        return period_label


# Output
class UserOuput(BaseModel):
    def see_results(self) -> bool:
        """
        Botton to visualize results
        """
        view_result = st.button(
            "Clicca qui per vedere la tipologia e la dimensione ottimale degli impianti che potresti installare i base ai tuoi consumi",
            key="visualize-result-multivettore",
            help="Questi valori sono stati calcolati attraverso un metodo di ottimizzazione basato sul gradiente, con lo scopo di minimizzare i costi (in un periodo di 20 anni) e di massimizzare la copertura dei consumi.",
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
        st.markdown(f"- un **impianto di cogenerazione** da {cogen_size} kW")

    def see_trigen_size(self, trigen_size: NonNegativeInt):
        st.markdown(f"- un **impianto di trigenerazione** da {trigen_size} kW")

    def see_battery_size(self, battery_size: NonNegativeInt):
        st.markdown(f"- un **impianto di accumulo** da {battery_size} kW")

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
        period_label=common.LabelPeriodLabelsList,
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

    def graph_return_investment(  # TODO: add attualizzazione dei costi
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
