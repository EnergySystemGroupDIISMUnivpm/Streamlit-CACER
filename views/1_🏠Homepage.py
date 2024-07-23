import streamlit as st
import sys
from pathlib import Path

src_path = str(Path(__file__).parents[1] / "src")
sys.path.append(src_path)

from Users_inputs import UserInput, CittadinoInput

# CONFIGURATION OF STREAMLIT PAGE
st.set_page_config(
    page_title="ENEA Simulatore CACER",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# DEFINITION OF SESSION STATE VARIABLES
if "user" not in st.session_state:
    st.session_state["user"] = ""
if "annual_consumption" not in st.session_state:
    st.session_state["annual_consumption"] = ""
if "region" not in st.session_state:
    st.session_state["region"] = ""
if "year_PV" not in st.session_state:
    st.session_state["year_PV"] = None
if "power_PV" not in st.session_state:
    st.session_state["power_PV"] = ""
if "area_PV" not in st.session_state:
    st.session_state["area_PV"] = ""
if "comune_under_5000" not in st.session_state:
    st.session_state["comune_under_5000"] = "No"
if "outcome_same_POD_cabin" not in st.session_state:
    st.session_state["outcome_same_POD_cabin"] = None
if "known_area" not in st.session_state:
    st.session_state["known_area"] = None
if "want_boosting" not in st.session_state:
    st.session_state["want_boosting"] = None


# title
st.markdown(
    "<h1 style='text-align: center; color: #0078AC;'><em>Benvenuto in</em> ENEA Simulatore CACER</h1>",
    unsafe_allow_html=True,
)

# body
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        "<h2 style='text-align: center; color: #0078AC;'>Step 1: Inserisci i dati richiesti</h2>",
        unsafe_allow_html=True,
    )
    users = ["Cittadino", "Amministratore di condominio", "Amministrazione pubblica"]
    st.session_state["user"] = st.selectbox(
        "Seleziona il tipo di utente", users, index=None
    )
    user_input = UserInput(f""" {st.session_state["user"]}""")

    # CITTADINO
    cittadino_input = CittadinoInput(f""" {st.session_state["user"]}""")
    if st.session_state["user"] == "Cittadino":
        st.session_state["annual_consumption"] = (
            cittadino_input.insert_annual_consumption()
        )
        st.session_state["region"] = cittadino_input.insert_region()
        (
            st.session_state["year_PV"],
            st.session_state["power_PV"],
            st.session_state["known_area"],
            st.session_state["area_PV"],
            st.session_state["comune_under_5000"],
            st.session_state["outcome_same_POD_cabin"],
        ) = cittadino_input.presence_or_construction_PV()
        if (
            st.session_state["known_area"] == "No"
        ):  # when user want to install PV but doesn't know area
            cittadino_input.visualize_results()
