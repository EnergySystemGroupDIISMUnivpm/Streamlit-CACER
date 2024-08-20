from enum import StrEnum

import streamlit as st


class MacroGroup(StrEnum):
    GruppoAutoconsumo = "Gruppo Autoconsumo"
    AutoconsumatoreADistanza = "Autoconsumatore a Distanza"
    ComunitaEnergetica = "Comunità Energetica"


def show_macro_group_selector() -> MacroGroup | None:
    macro_groups = [macro_group.value for macro_group in MacroGroup]
    choice = st.selectbox("Selezione gruppo", macro_groups, index=None)
    if choice is None:
        return None
    return MacroGroup(choice)
