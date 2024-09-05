import streamlit as st
from pydantic import BaseModel, ConfigDict, Field, AfterValidator, validate_call
import pandas as pd
import multivector_simulator.common as common


def title_multivettore():
    st.markdown(" ")
    st.markdown("## Simulatore Multivettore Energetico")


def read_excel_file(file_path):
    with open(file_path, "rb") as file:
        return file.read()


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
