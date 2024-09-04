import streamlit as st

from Multivettore_page import Simulator_Multivettore
from cacer_simulator.views.macro_selection import (
    MacroGroup,
    show_macro_group_selector,
    homepage,
    MacroSelection,
)
from CACER_page import Simulator_CACER


def main():
    macro_selection = homepage()

    match macro_selection:
        case MacroSelection.CACER:
            Simulator_CACER()
        case MacroSelection.Multivettore:
            Simulator_Multivettore()


if __name__ == "__main__":
    main()
