# TEST STREAMLIT: SELEZIONARE IL TIPO DI UTENTE E STAMPARLO
import streamlit as st

st.title("ENEA-CER")
utenti = ["Cittadino", "Amministratore di condominio", "Amministrazione pubblica"]
utente = st.selectbox("Seleziona il tipo di utente", utenti, index=None)
if utente != None:
    st.write(f"""L'utente selezionato è: {utente}""")
