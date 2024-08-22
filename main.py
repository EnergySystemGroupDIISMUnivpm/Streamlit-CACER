import streamlit as st

from cacer_simulator.views.homepage import MacroGroup, show_macro_group_selector
from cacer_simulator.views.view import UserInput
import controller_functions


def main():
    choice = show_macro_group_selector()

    match choice:
        case MacroGroup.AutoconsumatoreADistanza:
            st.toast("SELECTED: Autoconsumatore a distanza", icon="💡")
        case MacroGroup.ComunitaEnergetica:
            st.toast("SELECTED: Comunità Energetica", icon="💡")
            user_input = UserInput()
            region = user_input.insert_region()
            inhabitants = user_input.municipality()
            know_cer_members = user_input.cer_with()
            if know_cer_members == "Si":
                knowledge_cer_consumption = user_input.know_members_consumption()
                if knowledge_cer_consumption == "No":
                    members = user_input.insert_members()
                    area, year_pv, power_pv = controller_functions.info_pv_or_area(
                        user_input
                    )
                elif knowledge_cer_consumption == "Si":
                    consumption = user_input.insert_annual_consumption(
                        "Inserisci i consumi annui totali, in kwh, della tua CER "
                    )
                    percentage_daily_consumption = (
                        user_input.insert_percentage_daytime_consumption()
                    )
                    area, year_pv, power_pv = controller_functions.info_pv_or_area(
                        user_input
                    )

        case MacroGroup.GruppoAutoconsumo:
            st.toast("SELECTED: Gruppo Autoconsumo", icon="💡")


if __name__ == "__main__":
    main()
