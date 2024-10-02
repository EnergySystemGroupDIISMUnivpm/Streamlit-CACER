import streamlit as st
from pydantic import BaseModel, ConfigDict, Field, AfterValidator, validate_call
import pandas as pd
import numpy as np
from cacer_simulator.common import PositiveOrZeroFloat
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


class UserOuput(BaseModel):
    def see_results(self) -> bool:
        view_result = st.button(
            "Clicca qui per vedere la tipologia e la dimensione ottimale degli impianti che potresti installare i base ai tuoi consumi",
            key="visualize-result-multivettore",
            help="Questi valori sono stati calcolati attraverso un metodo di ottimizzazione basato sul gradiente, con lo scopo di minimizzare i costi (in un periodo di 20 anni) e di massimizzare la copertura dei consumi.",
        )

        return view_result

    def see_pv_size(self, pv_size: NonNegativeInt):
        if pv_size > 0:
            st.markdown(
                f"**La dimensione ottimale dell'impianto fotovoltaico:** {pv_size} kW"
            )

    def see_cogen_size(self, cogen_size: NonNegativeInt):
        if cogen_size > 0:
            st.markdown(
                f"**La dimensione ottimale dell'impianto di cogenerazione:** {cogen_size} kW"
            )

    def battery_size(self, battery_size: NonNegativeInt):
        if battery_size > 0:
            st.markdown(
                f"**La dimensione ottimale del sistema di accumolo:** {battery_size} kW"
            )

    def see_coverage_energy_plot(
        self, consumed_energy: np.ndarray, produced_energy: np.ndarray
    ):
        ore = np.arange(len(consumed_energy))

        data_to_be_plotted = pd.DataFrame(
            {
                "energia_consumata": consumed_energy,
                "energia_autoprodotta": produced_energy,
                "ore": ore,
            }
        )
        st.area_chart(data_to_be_plotted.set_index("ore"))
