from enum import StrEnum

import streamlit as st


class MacroGroup(StrEnum):
    GruppoAutoconsumo = "Gruppo Autoconsumo"
    AutoconsumatoreADistanza = "Autoconsumatore a Distanza"
    ComunitaEnergetica = "Comunità Energetica"


def show_macro_group_selector() -> MacroGroup | None:
    macro_groups = [macro_group.value for macro_group in MacroGroup]
    choice = st.selectbox(
        "Seleziona una delle tre tipologie di CACER",
        macro_groups,
        index=None,
        key="Type CACER selection",
    )
    
    if choice is None:
        return None
    return MacroGroup(choice)
    

class MacroSelection(StrEnum):
    CACER = "CACER"
    Multivettore = "Multivettore energetico"


def homepage() -> MacroSelection | None:
    st.title("Benvenuto in ENEA Simulatore CACER e Multivettore Energetico")

    col1, col2 = st.columns(2)
    
    # Usare session_state per memorizzare la selezione
    if 'selection' not in st.session_state:
        st.session_state['selection'] = None

    # Sezione CACER
    with col1:
        st.header("CACER")
        st.write("Questa sezione contiene una spiegazione dettagliata delle CACER.")
        if st.button("CACER Simulatore"):
            st.session_state['selection'] = MacroSelection.CACER

    # Sezione Multivettore energetico
    with col2:
        st.header("Multivettore energetico")
        st.write("Simulatore per i sistemi multivettore energetici.")
        if st.button("Multivettore Simulatore"):
            st.session_state['selection'] = MacroSelection.Multivettore

    return st.session_state['selection']
