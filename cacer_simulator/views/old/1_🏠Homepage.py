import streamlit as st
import sys
from pathlib import Path

src_path = str(Path(__file__).parents[1] / "src")
sys.path.append(src_path)

from Users_inputs import UserInput, CittadinoInput
from session_state_variables import default_values_homepage
import streamlit_pages_configuration

# page configuration
streamlit_pages_configuration.configuration()
streamlit_pages_configuration.home_page_title()

# DEFINITION OF SESSION STATE VARIABLES
for key, value in default_values_homepage.items():
    if key not in st.session_state:
        st.session_state[key] = value

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
        st.session_state["percentage_daytime"] = (
            cittadino_input.insert_percentage_daytime_consumption()
        )
        st.session_state["region"] = cittadino_input.insert_region()

        (
            st.session_state["year_PV"],
            st.session_state["power_PV"],
            st.session_state["boosting_power"],
            st.session_state["known_area"],
            st.session_state["area_PV"],
            st.session_state["comune_under_5000"],
            st.session_state["user_CACER_choice"],
        ) = cittadino_input.presence_or_construction_PV()
