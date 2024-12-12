from enum import StrEnum

import streamlit as st


class MacroGroup(StrEnum):
    GruppoAutoconsumo = "Gruppo Autoconsumo"
    AutoconsumatoreADistanza = "Autoconsumatore a Distanza"
    ComunitaEnergetica = "Comunità Energetica"


def show_macro_group_selector() -> MacroGroup | None:
    macro_groups = [macro_group.value for macro_group in MacroGroup]
    choice = st.selectbox(
        "Seleziona una delle tre possibili configurazioni di CACER",
        macro_groups,
        index=None,
        key="Type CACER selection",
        placeholder="Seleziona un'opzione",
    )

    if choice is None:
        return None
    return MacroGroup(choice)
