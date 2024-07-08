import streamlit as st
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)
from Users_inputs import User_input, Cittadino_input



#CONFIGURATION OF STREAMLIT PAGE
st.set_page_config(
    page_title="ENEA Simulatore CACER",
    page_icon="🌤️",
    layout='wide',
    initial_sidebar_state='collapsed'
    )   

#DEFINITION OF SESSION STATE VARIABLES
if "user" not in st.session_state:
    st.session_state["user"]=None
if "annual_consumption" not in st.session_state:
    st.session_state["annual_consumption"]=None
if "region" not in st.session_state:
    st.session_state["region"]=None
if "year_PV" not in st.session_state:
    st.session_state["year_PV"]=None
if "power_PV" not in st.session_state:
    st.session_state["power_PV"]=None
if "area_PV" not in st.session_state:
    st.session_state["area_PV"]=None
if "comune_under_5000" not in st.session_state:
    st.session_state["comune_under_5000"]="No"
if "outcome_same_POD_cabin" not in st.session_state:
    st.session_state["outcome_same_POD_cabin"]=""



#title
st.markdown("<h1 style='text-align: center; color: #0078AC;'><em>Benvenuto in</em> ENEA Simulatore CACER</h1>", unsafe_allow_html=True)

#body
col1,col2,col3=st.columns([1, 2, 1])
with col2:
    st.markdown("<h2 style='text-align: center; color: #0078AC;'>Step 1: Inserisci i dati richiesti</h2>", unsafe_allow_html=True)
    users=["Cittadino","Amministratore di condominio","Amministrazione pubblica"]
    st.session_state["user"]=st.selectbox("Seleziona il tipo di utente",users,index=None)
    user_input=User_input(f""" {st.session_state["user"]}""")
    st.session_state["annual_consumption"]=user_input.insert_annual_consumption()
    st.session_state["region"]=user_input.insert_region()
    st.session_state["year_PV"],st.session_state["power_PV"],st.session_state["area_PV"],st.session_state["comune_under_5000"]=user_input.presence_or_construction_PV()
    if st.session_state["user"]=="Cittadino":
        if st.session_state["area_PV"]!=None:
            st.session_state["outcome_same_POD_cabin"]=Cittadino_input.area_same_POD_and_cabin_house(st.session_state["area_PV"],st.session_state["region"])
            print(f""" {st.session_state["outcome_same_POD_cabin"]}""")
    
                    
        


   