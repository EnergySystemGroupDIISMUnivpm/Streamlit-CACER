import streamlit as st

from cacer_simulator.views.homepage import MacroGroup, show_macro_group_selector
from cacer_simulator.views.view import UserInput


def main():
    choice = show_macro_group_selector()

    match choice:
        case MacroGroup.AutoconsumatoreADistanza:
            st.toast("SELECTED: Autoconsumatore a distanza", icon="💡")
        case MacroGroup.ComunitaEnergetica:
            st.toast("SELECTED: Comunità Energetica", icon="💡")
        case MacroGroup.GruppoAutoconsumo:
            st.toast("SELECTED: Gruppo Autoconsumo", icon="💡")


if __name__ == "__main__":
    main()
