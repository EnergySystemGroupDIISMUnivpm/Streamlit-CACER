import streamlit as st
from pydantic import PositiveFloat, validate_call, BaseModel
import pandas as pd


def title_multivettore():
    st.markdown(" ")
    st.markdown("## Simulatore Multivettore Energetico")


def read_excel_file(file_path):
    with open(file_path, "rb") as file:
        return file.read()


class UserInput(BaseModel):

    def download_upload_consumption(self) -> pd.DataFrame | None:
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

            st.write("Contenuto del file Excel caricato:")
            st.dataframe(df_uploaded)
            return df_uploaded
