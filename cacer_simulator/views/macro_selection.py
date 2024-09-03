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
    selection = None
    # Sezione CACER nella colonna di sinistra
    with col1:
        st.header("CACER")
        st.write(
            """
            Questa sezione contiene una spiegazione dettagliata delle  CACER 
        """
        )
        if st.button("CACER Simulatore"):
            selection = MacroSelection.CACER

    # Sezione Multivettore energetico nella colonna di destra
    with col2:
        st.header("Multivettore energetico")
        st.write(
            """
            Questa sezione si concentra sulla simulazione di sistemi multivettore energetici. 
            Questi sistemi integrano diverse fonti energetiche per ottimizzare la produzione 
            e distribuzione di energia. Qui puoi eseguire simulazioni per valutare l'efficienza
            e la sostenibilità dei sistemi multivettore.
        """
        )
        if st.button("Multivettore Simulatore"):
            selection = MacroSelection.Multivettore
    return selection
