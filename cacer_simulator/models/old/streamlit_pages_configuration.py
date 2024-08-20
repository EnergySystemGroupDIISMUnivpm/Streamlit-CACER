from pathlib import Path

import streamlit as st

resources_path = Path(__file__).parents[1] / "resources"

path_logo_enea = resources_path / "logo_ENEA.png"
path_logo_univpm = resources_path / "logo_UNIVPM.png"
simulatore_nome = "ENEA Simulatore CACER"


# CONFIGURATION OF STREAMLIT PAGE
def configuration():
    st.set_page_config(
        page_title="ENEA Simulatore CACER",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # titles


def home_page_title():
    st.markdown(
        f"""<h1 style='text-align: center; color: #0078AC;'><em>Benvenuto in</em> {simulatore_nome}""",
        unsafe_allow_html=True,
    )


def Risultati_title():
    st.markdown(
        f"""<h1 style='text-align: center; color: #0078AC;'> {simulatore_nome}: qui puoi visualizzare i tuoi risultati</em></h1>""",
        unsafe_allow_html=True,
    )


def attention():
    st.markdown(
        """
    <style>
    .bottom-right {
        position: fixed;
        bottom: 10px;
        right: 30px;
        padding: 10px;
        background-color: rgba(255, 255, 255, 0.7);
    }
    </style>
    <div class="bottom-right">
        Attenzione! Tutti i dati che vedi sono da intendersi come stime.
            </div>
    """,
        unsafe_allow_html=True,
    )
