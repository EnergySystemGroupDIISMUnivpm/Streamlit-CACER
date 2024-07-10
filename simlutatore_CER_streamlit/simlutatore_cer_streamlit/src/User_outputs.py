import streamlit as st
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)
import computations

class User_output():
    def __init__(self, type):
        self.name = type
    def comput_annual_production(area_PV,region):
        annual_production=int(computations.computation_annual_production(area_PV,region))
        st.markdown(f"""- Con i dati che hai fornito, potresti costuire un impianto PV che potrebbe generare un **quantitativo di energia elettrica in un anno** pari a {annual_production} kWh/anno""")
        return annual_production
    def comput_cost_plant(area_PV):
        impiant_cost=int(computations.computation_installation_cost(area_PV))
        st.markdown(f"""- **Il costo dell'installazione** dell'impianto sarebbe approssimatamente {impiant_cost} €""")
        return impiant_cost
    def optimal_dimension(annual_comsumption,region):
        optimal_dim=int(computations.computation_optimal_dimension(annual_comsumption,region))
        st.markdown(f"""- **L'area ottima**  del tuo impianto sarebbe di {optimal_dim} m²""")
        return optimal_dim

class Cittadino_output(User_output):
    def visualize_results_from_same_POD_and_cabin(self,outcome,area_PV,region):
        if str(outcome)=="Calculate_cost_and_production":
            annual_production=int(self.comput_annual_production(area_PV,region))
            return annual_production

