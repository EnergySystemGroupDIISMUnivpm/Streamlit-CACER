import streamlit as st
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)
import User_outputs

#CONFIGURATION OF STREAMLIT PAGE
st.set_page_config(
    page_title="ENEA Simulatore CACER",
    page_icon="🌤️",
    layout='wide',
    initial_sidebar_state='collapsed'
    )   

#session state variables
if "annual production" not in st.session_state:
    st.session_state["annual production"]=""
if "impiant_cost" not in st.session_state:
    st.session_state["impiant_cost"]=""
if "optimal_dim" not in st.session_state:
     st.session_state["optimal_dim"]=""
if "power_peak" not in st.session_state:
      st.session_state["power_peak"]=""
if "overproduction" not in st.session_state:
      st.session_state["overproduction"]=""
if "benefit" not in st.session_state:
      st.session_state["benefit"]=""
if "avg_time_overproduction" not in st.session_state:
     st.session_state["avg_time_overproduction"]=""
if "self_consump" not in st.session_state:
     st.session_state["self_consump"]=""


#title 
st.markdown("<h1 style='text-align: center; color: #0078AC;'> ENEA Simulatore CACER <em>: qui puoi visualizzare i tuoi risultati</em></h1>", unsafe_allow_html=True)

#information at the bottom right
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
    unsafe_allow_html=True
)

#FOR ALL USERS
user_output=User_outputs.User_output(f"""{st.session_state["user"]}""")

#CITTADINO
if st.session_state["user"]=="Cittadino":
    cittadino_output=User_outputs.Cittadino_output(f"""{st.session_state["user"]}""")
    if st.session_state["year_PV"]==None: #the user doesn't have PV
        if st.session_state["known_area"]=="No": #if user want to be build a PV but doesn't know where
            st.session_state["optimal_dim"]=cittadino_output.optimal_dimension(st.session_state["annual_consumption"],st.session_state["region"])
            st.session_state["annual production"],st.session_state["power_peak"]=cittadino_output.comput_annual_production_and_power_peak(st.session_state["optimal_dim"],
                                                                                                                                                            st.session_state["region"])
            st.session_state["impiant_cost"]= cittadino_output.comput_cost_plant(st.session_state["power_peak"])
            st.session_state["self_consump"]= cittadino_output.self_consumption(
                    st.session_state["annual_consumption"],
                    st.session_state["region"],
                    st.session_state["power_peak"])
            st.session_state["overproduction"]=cittadino_output.overproduction(st.session_state["annual production"],
                                                                                st.session_state["self_consump"])
            st.session_state["benefit"]=cittadino_output.CACER_benefit(st.session_state["overproduction"],
                                                                        st.session_state["self_consump"],
                                                                        st.session_state["power_peak"],
                                                                        st.session_state["region"],
                                                                        st.session_state["comune_under_5000"])

        if st.session_state["outcome_same_POD_cabin"]!=None: #when the user knows the area where to install PV and all inputs have been inserted
                st.session_state["annual production"], st.session_state["power_peak"],st.session_state["impiant_cost"],st.session_state["self_consump"],st.session_state["overproduction"],st.session_state["benefit"]= cittadino_output.visualize_results_from_same_POD_and_cabin(
                    st.session_state["outcome_same_POD_cabin"], 
                    st.session_state["area_PV"], 
                    st.session_state["region"],
                    st.session_state["annual_consumption"],
                    st.session_state["comune_under_5000"])
            
                

