import streamlit as st

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
            pass


if __name__ == "__main__":
    main()
