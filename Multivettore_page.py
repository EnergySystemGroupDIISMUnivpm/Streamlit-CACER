import streamlit as st
import pandas as pd


def read_excel_file(file_path):
    with open(file_path, "rb") as file:
        return file.read()


def Simulator_Multivettore():
    st.markdown("**Scarica, Compila e Ricarica un File Excel**")

    # Step 1: Fornire il file Excel esistente per il download
    # Specifica il percorso del file Excel che vuoi rendere disponibile per il download
    file_path = "resources/Esempio_input_consumi_multienergetico.xlsx"

    # Funzione per leggere il file già esistente

    # Bottone per scaricare il file Excel esistente
    st.download_button(
        label="Scarica il file Excel",
        data=read_excel_file(file_path),
        file_name="Esempio_input_consumi_multienergetico.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Step 2: Carica il file Excel compilato dall'utente
    uploaded_file = st.file_uploader("Carica il file Excel compilato", type=["xlsx"])

    # Step 3: Visualizza il file Excel caricato
    if uploaded_file is not None:
        df_uploaded = pd.read_excel(uploaded_file, engine="openpyxl")

        # Mostra i dati caricati
        st.write("Contenuto del file Excel caricato:")
        st.dataframe(df_uploaded)

        # Opzionalmente puoi fare ulteriori elaborazioni o salvare il file
        # Ad esempio, puoi applicare validazioni o modifiche ai dati
