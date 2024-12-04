import streamlit as st

from Multivettore_page_controller import Simulator_Multivettore
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
    if "cache_cleared" not in st.session_state:
        st.cache_data.clear()  # Clear cache on page refresh
        st.session_state.cache_cleared = True  # Mark cache as cleared
    main()
