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
if "user_output" not in st.session_state:
    st.session_state["user_output"]=""
if "impiant_cost" not in st.session_state:
    st.session_state["impiant_cost"]=""
if "optimal_dim" not in st.session_state:
     st.session_state["optimal_dim"]=""

#title 
st.markdown("<h1 style='text-align: center; color: #0078AC;'> ENEA Simulatore CACER <em>: qui puoi visualizzare i tuoi risultati</em></h1>", unsafe_allow_html=True)



#body
#FOR ALL USERS
print(f""""{st.session_state["known_area"]}""")
if st.session_state["known_area"]=="No": #if user want to be build a PV but doesn't know where
          st.session_state["optimal_dim"]=User_outputs.User_output.optimal_dimension(st.session_state["annual_consumption"],st.session_state["region"])

#CITTADINO
if st.session_state["user"]=="Cittadino":
    st.session_state["user_output"]=User_outputs.Cittadino_output(f"""{st.session_state["user"]}""")
    if st.session_state["outcome_same_POD_cabin"]!="": #when the user knows the area where to install PV and all inputs have been inserted
            st.session_state["annual production"]=st.session_state["user_output"].visualize_results_from_same_POD_and_cabin(st.session_state["outcome_same_POD_cabin"], st.session_state["area_PV"], st.session_state["region"])
            st.session_state["impiant_cost"]=User_outputs.Cittadino_output.comput_cost_plant(st.session_state["area_PV"])


