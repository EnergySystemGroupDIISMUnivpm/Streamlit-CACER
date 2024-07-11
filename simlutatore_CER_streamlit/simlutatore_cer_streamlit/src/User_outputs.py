import streamlit as st
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)
import computations

class User_output():
    def __init__(self, type):
        self.name = type

    def comput_annual_production(self,area_PV,region):
        annual_production,installable_power=computations.computation_annual_production(area_PV,region)
        annual_production=int(annual_production)
        installable_power=int(installable_power)
        st.markdown(f"""- Con i dati che hai fornito, potresti costuire un impianto PV da {installable_power} kW di **potenza di picco** e che potrebbe generare un **quantitativo di energia elettrica in un anno** pari a {annual_production} kWh/anno""")
        return annual_production, installable_power
    
    def comput_cost_plant(self,area_PV):
        impiant_cost=int(computations.computation_installation_cost(area_PV))
        st.markdown(f"""- **Il costo dell'installazione** dell'impianto sarebbe approssimatamente {impiant_cost} €""")
        return impiant_cost
    
    def optimal_dimension(self,annual_comsumption,region):
        optimal_dim=int(computations.computation_optimal_dimension(annual_comsumption,region))
        st.markdown(f"""- **L'area ottima**  del tuo impianto sarebbe di {optimal_dim} m²""")
        return optimal_dim
    
    def self_consumption(self,annual_comsumption,region,power_peak):
        self_consump=int(computations.computation_self_consump(annual_comsumption,region,power_peak))
        st.markdown(f"""- Abbiamo stimato che **autoconsumeresti in media**  {self_consump} kWh/anno""")
        return self_consump
    
    def overproduction(self,annual_production,self_consumption):
        overproduction=int(computations.comp_if_there_is_overproduction(annual_production,self_consumption))
        if overproduction>0:
         st.markdown(f"""- Abbiamo stimato che potresti costuire un impianto che ti farebbe raggiungere {overproduction} kWh/anno di **sovraproduzione**""")
        return overproduction

 
class Cittadino_output(User_output):
    def __init__(self, type):
        super().__init__(type)  
        
    def visualize_results_from_same_POD_and_cabin(self,outcome,area_PV,region):
        if str(outcome)=="Calculate_cost_and_production":
            annual_production,power_peak=self.comput_annual_production(area_PV,region)
            return annual_production,power_peak

