import streamlit as st
import streamlit_pages_configuration
import User_outputs
from session_state_variables import default_values_Risultati

# CONFIGURATION OF STREAMLIT PAGE
streamlit_pages_configuration.configuration()
streamlit_pages_configuration.Risultati_title()
streamlit_pages_configuration.attention()

# session state variables
for key, value in default_values_Risultati.items():
    if key not in st.session_state:
        st.session_state[key] = value

# FOR ALL USERS
user_output = User_outputs.User_output(f"""{st.session_state["user"]}""")

# CITTADINO
if st.session_state["user"] == "Cittadino":
    cittadino_output = User_outputs.Cittadino_output(f"""{st.session_state["user"]}""")
    if st.session_state["year_PV"] == None:  # the user doesn't have PV
        if (
            st.session_state["known_area"] == "No"
        ):  # if user want to be build a PV but doesn't know where
            st.session_state["optimal_dim"] = cittadino_output.optimal_dimension(
                st.session_state["annual_consumption"],
                st.session_state["region"],
                st.session_state["percentage_daytime"],
            )

            st.session_state["annual production"], st.session_state["power_peak"] = (
                cittadino_output.comput_annual_production_from_area_and_power_peak(
                    st.session_state["optimal_dim"], st.session_state["region"]
                )
            )

            st.session_state["impiant_cost"] = cittadino_output.comput_cost_plant(
                st.session_state["power_peak"]
            )
            st.session_state["benefit"] = (
                cittadino_output.savings_bolletta_from_PV_construction(
                    st.session_state["annual_consumption"]
                )
            )
            cittadino_output.info_possibility_CER()
            cittadino_output.visit_FAQ()

        if (
            st.session_state["user_CACER_choice"] != None
        ):  # when the user knows the area where to install PV
            (
                st.session_state["annual production"],
                st.session_state["power_peak"],
                st.session_state["impiant_cost"],
                st.session_state["self_consump"],
                st.session_state["overproduction"],
                st.session_state["benefit"],
                st.session_state["members"],
            ) = cittadino_output.results_from_user_CACER_choice(
                st.session_state["user_CACER_choice"],
                st.session_state["area_PV"],
                st.session_state["power_PV"],
                st.session_state["year_PV"],
                st.session_state["boosting_power"],
                st.session_state["region"],
                st.session_state["percentage_daytime"],
                st.session_state["annual_consumption"],
                st.session_state["comune_under_5000"],
            )

    if st.session_state["year_PV"] != None:  # the user has PV
        (
            st.session_state["annual production"],
            st.session_state["power_peak"],
            st.session_state["impiant_cost"],
            st.session_state["self_consump"],
            st.session_state["overproduction"],
            st.session_state["benefit"],
            st.session_state["members"],
        ) = cittadino_output.results_from_user_CACER_choice(
            st.session_state["user_CACER_choice"],
            st.session_state["area_PV"],
            st.session_state["power_PV"] + st.session_state["boosting_power"],
            st.session_state["year_PV"],
            st.session_state["boosting_power"],
            st.session_state["region"],
            st.session_state["percentage_daytime"],
            st.session_state["annual_consumption"],
            st.session_state["comune_under_5000"],
        )
