import streamlit as st
import sys
<<<<<<< HEAD
from pathlib import Path

src_path = str(Path(__file__).parents[1] / "src")
sys.path.append(src_path)

from Users_inputs import UserInput, CittadinoInput

# CONFIGURATION OF STREAMLIT PAGE
=======
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'enea-simulatore-cer'))

# Aggiungi la directory 'src' al percorso di ricerca dei moduli
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)
print(sys.path, "-------------", src_path)

from session_state_variables import default_values_homepage
from Users_inputs import User_input, Cittadino_input

#CONFIGURATION OF STREAMLIT PAGE
>>>>>>> faaaf49 (moved streamlit state variables to another file)
st.set_page_config(
    page_title="ENEA Simulatore CACER",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

<<<<<<< HEAD
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
=======
#DEFINITION OF SESSION STATE VARIABLES
for key, value in default_values_homepage.items():
    if key not in st.session_state:
        st.session_state[key] = value
>>>>>>> faaaf49 (moved streamlit state variables to another file)


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
