import streamlit as st
from typing import Tuple
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)
import computations
import CACER_config

#definition of class with methods in common with all users
class User_output():
    def __init__(self, type):
        self.name = type

    def comput_annual_production_and_power_peak(self,area_PV:int,region:str)->Tuple[int, int]:
        annual_production,installable_power=computations.computation_annual_production(area_PV,region)
        annual_production=int(round(annual_production))
        installable_power=int(round(installable_power))
        st.markdown(f"""- Con i dati che hai fornito, potresti costuire un impianto PV da {installable_power} kWp di **potenza di picco** e che potrebbe generare un **quantitativo di energia elettrica in un anno** pari a {annual_production} kWh/anno""")
        return annual_production, installable_power

    
    def comput_cost_plant(self,area_PV:int)->int:
        impiant_cost=int(round(computations.computation_installation_cost(area_PV)))
        st.markdown(f"""- **Il costo dell'installazione** dell'impianto sarebbe approssimatamente {impiant_cost} €""")
        return impiant_cost
    
    def optimal_dimension(self,annual_comsumption:int,region:str)->int:
        optimal_dim=int(round(computations.computation_optimal_dimension(annual_comsumption,region)))
        st.markdown(f"""- **L'area ottima**  del tuo impianto sarebbe di {optimal_dim} m²""")
        return optimal_dim
    
    def self_consumption(self,annual_comsumption:int,region:str,power_peak:int)->int:
        self_consump=int(round(computations.computation_self_consump(annual_comsumption,region,power_peak)))
        st.markdown(f"""- Abbiamo stimato che **autoconsumeresti in media**  {self_consump} kWh/anno""")
        return self_consump
    
    def overproduction(self,annual_production:int,self_consumption:int)->int:
        overproduction=int(round(computations.comp_if_there_is_overproduction(annual_production,self_consumption)))
        if overproduction>0:
         st.markdown(f"""- Abbiamo stimato che potresti costuire un impianto che ti farebbe raggiungere {overproduction} kWh/anno di **sovraproduzione**""")
        return overproduction
    
    def visit_FAQ(self):
        st.markdown("""<br>""",unsafe_allow_html=True)         
        st.markdown("""Per maggiori informazioni visita la sezione *❓FAQ*""")
    
    def CO2_reducted(self,energy_self_consum:int|float):
        CO2=int(round(computations.computation_reduced_CO2(energy_self_consum)))
        st.markdown(f"""- Inoltre ridurresti la tua **produzione di CO2** di {CO2} kg CO2/kWh""")
        return CO2
    def enter_or_create_CER(self,benefit:float|int):
        st.markdown(f"""- Valuta la possibilità di entrare a fare parte o creare una **CER**, potresti ricevere fino a **{benefit}€** all'anno di incentivi""")
    def enter_or_create_Group(self,benefit:float|int):
        st.markdown(f"""- Valuta la possibilità di entrare a fare parte o creare un **Gruppo di Autoconsumatori**, potresti ricevere fino a **{benefit}€** all'anno di incentivi""")
    def create_Self_consum(self,benefit:float|int):
        st.markdown(f"""- Valuta la possibilità di diventare un **Autoconsumatore a distanza**, potresti ricevere fino a **{benefit}€** all'anno di incentivi""")

#user: "Cittadino"     
class Cittadino_output(User_output):
    def __init__(self, type):
        super().__init__(type)  
        
   
    def visualize_results_from_same_POD_and_cabin(self,outcome:str,area_PV:int,region:str)->Tuple[int,int]:
         if str(outcome)=="Calculate_cost_and_production":
            annual_production,power_peak=self.comput_annual_production_and_power_peak(area_PV,region)
            return annual_production,power_peak
        
    def CACER_benefit(self,overproduction:int,energy_self_consum:int|float,implant_power:int|float,region:str,comune:str)->Tuple[int|float,int|float]:
        if overproduction>0:
            CER=CACER_config.CER("CER")
            benefit=CER.total_benefit(energy_self_consum,implant_power,region,comune)
            self.enter_or_create_CER(benefit)
        elif overproduction<=0:
            Group=CACER_config.groups_self_consumers("Group of self consumer")
            benefit=Group.total_benefit(energy_self_consum,implant_power,region,comune)
            self.enter_or_create_Group(benefit)
        CO2=self.CO2_reducted(energy_self_consum)
        self.visit_FAQ()
        return benefit,CO2


