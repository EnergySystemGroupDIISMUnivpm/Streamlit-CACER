import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from Users import User

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




st.markdown("<h1 style='text-align: center; color: #0078AC;'><em>Benvenuto in</em> ENEA Simulatore CACER</h1>", unsafe_allow_html=True)

col1,col2,col3=st.columns([1, 2, 1])
with col2:
    st.markdown("<h2 style='text-align: center; color: #0078AC;'>Step 1: Inserisci i dati richiesti</h2>", unsafe_allow_html=True)
    users=["Cittadino","Amministratore di condominio","Amministrazione pubblica"]
    st.session_state["user"]=st.selectbox("Seleziona il tipo di utente",users,index=None)
    user=User(f""" {st.session_state["user"]}""")
    st.session_state["annual_consumption"]=user.insert_annual_consumption()
    st.session_state["region"]=user.insert_region()
    st.session_state["year_PV"],st.session_state["power_PV"],st.session_state["area_PV"],st.session_state["comune_under_5000"]=user.presence_or_construction_PV()



   