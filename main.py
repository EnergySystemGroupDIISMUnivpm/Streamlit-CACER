import streamlit as st

from Multivettore_page_controller import Simulator_Multivettore
from cacer_simulator.views.macro_selection import (
    MacroGroup,
    show_macro_group_selector,
)
from views.view_homepage import homepage, MacroSelection
from CACER_page_controller import Simulator_CACER


def main():
    """opening of homepage and selection of CACER simulator or Multivector simulator"""
    macro_selection = homepage()

    match macro_selection:
        case MacroSelection.CACER:
            Simulator_CACER()
        case MacroSelection.Multivettore:
            Simulator_Multivettore()


if __name__ == "__main__":
    main()
