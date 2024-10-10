from msilib import type_binary
import streamlit as st
from pydantic import BaseModel, ConfigDict, Field, AfterValidator, validate_call
import pandas as pd
import numpy as np
from cacer_simulator.common import PositiveOrZeroFloat
import multivector_simulator.common as common
from pydantic import PositiveFloat, validate_call, PositiveInt, NonNegativeInt
import plotly.graph_objects as go
from datetime import datetime


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
        df_uploaded = None
        st.markdown(
            "Scarica, Compila con i tuoi consumi energetici e Ricarica il File Excel. Il file deve contenere i consumi elettrici, caloriferi e frigoriferi orari riferiti ad un periodo di un anno."
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
                df_uploaded = common.validate_consumption_dataframe(df_uploaded)
                st.success("Contenuto del file Excel caricato con successo:")
                st.dataframe(df_uploaded)
            except ValueError as e:
                st.error(f"Errore di validazione: {e}")
                return None
            return df_uploaded

        return None

    def select_period_plot(self):
        period_label=None
        period_label=st.radio(
            "Seleziona il periodo in cui visualizzare la distribuzione media della tua energia",
            options=list(common.PERIOD_TO_BE_PLOTTED.keys()), index=None, key="select label of period"
        )
        return period_label

    
# Output
class UserOuput(BaseModel):
    def see_results(self) -> bool:
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
        if battery_size > 0:
            self.see_battery_size(battery_size)

    def see_pv_size(self, pv_size: NonNegativeInt):
        st.markdown(f"- un **impianto fotovoltaico** da {pv_size} kW")

    def see_cogen_size(self, cogen_size: NonNegativeInt):
        st.markdown(f"- un **impianto di cogenerazione** da {cogen_size} kW")

    def see_battery_size(self, battery_size: NonNegativeInt):
        st.markdown(f"- un **impianto di accumulo** da {battery_size} kW")

    
    def extract_period_from_period_label(self, period_label:str)->int:
        period = common.PERIOD_TO_BE_PLOTTED[period_label]
        return period
    
    def see_coverage_energy_plot(
        self,
        consumed_energy: np.ndarray,
        produced_energy: np.ndarray,
  
        energy_type: str,
        period_label="str"
    ):
        ore = np.arange(len(consumed_energy))
        chart_data = pd.DataFrame(
    {
        "Ore": ore,
        "Energia consumata": consumed_energy,
        "Energia prodotta": produced_energy,
       
    }
)       
        
        st.markdown(f"""Distribuzione media dell'energia {energy_type} {period_label}""")
        st.area_chart(chart_data, x = "Ore")

    def see_costs_investment_recovery(
        self, costs: PositiveFloat, recovery_time: PositiveInt
    ):
        st.markdown(
            f"Il costo previsto per l'installazione degli impianti è di circa {costs}€. Grazie all'energia autoprodotta, riusciresti a recuperare l'investimento in circa {recovery_time} anni.",
            help=f"Il tempo di recupero è stato calcolato tenendo conto di un prezzo dell'energia elettrica da rete pari a {common.ELECTRIC_ENERGY_PRICE}€/kWh, un costo dell'energia termica da rete pari a {common.THERMAL_ENERGY_PRICE}€/kWh e un costo del carburante per il cogeneratore pari a {common.COST_GAS_FOR_GEN}€/Smc.",
        )

    def see_environmental_benefit(self, reduced_CO2: PositiveFloat):
        st.markdown(
            f"Attraverso l'uso e l'installazione di questi impianti ridurresti le emissioni di circa {reduced_CO2} kg CO2 ogni anno.",
            help="Questi dati sono stati calcolati utilizzando il fattore di emissione medio riportato dall'Ispra per il 2022.",
        )

    