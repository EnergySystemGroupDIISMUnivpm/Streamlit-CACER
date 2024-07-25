import streamlit as st
from typing import Tuple
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)
import computations
import CACER_config
import pandas as pd

#definition of class with methods in common with all users
class User_output():
    def __init__(self, type):
        self.name = type
    def visit_FAQ(self):
        st.markdown("Per maggiorni informazioni visita la sezione ❓FAQ")

    def comput_annual_production_from_area_and_power_peak(self,area_PV:int,region:str)->Tuple[int, int]:
        annual_production,installable_power=computations.computation_annual_production_from_area(area_PV,region)
        annual_production=int(round(annual_production))
        installable_power=int(round(installable_power))
        st.markdown(f"""- Con i dati che hai fornito, potresti costuire un impianto PV da {installable_power} kWp di **potenza di picco** e che potrebbe generare un **quantitativo di energia elettrica in un anno** pari a {annual_production} kWh/anno""")
        return annual_production, installable_power
    
    def comput_annual_production_from_power(self,power:int|float,region:str)->int|float:
        annual_production=int(round(computations.computation_annual_production_from_power(power,region)))
        st.markdown(f"""- Con il tuo impianto potresti produrre circa **{annual_production} kWh** all'anno""")
        return annual_production

    
    def comput_cost_plant(self,installable_power:int|float)->int:
        impiant_cost=int(round(computations.computation_installation_cost(installable_power)))
        st.markdown(f"""- **Il costo dell'installazione** dell'impianto sarebbe approssimatamente {impiant_cost} €""")
        return impiant_cost
    
    def optimal_dimension(self,annual_comsumption:int,region:str,percentage_daytime_consum:str)->int:
        optimal_dim=int(round(computations.computation_optimal_dimension(annual_comsumption,region,percentage_daytime_consum)))
        st.markdown(f"""- **L'area ottima**  del tuo impianto sarebbe di {optimal_dim} m²""")
        return optimal_dim
    
    def self_consumption(self,annual_comsumption:int,percentage_daily_consump: float, annual_production: int | float)->int|float:
        self_consump=int(round(computations.computation_self_consump(annual_comsumption,percentage_daily_consump,annual_production)))
        st.markdown(f"""- Abbiamo stimato che **autoconsumeresti in media**  {self_consump} kWh/anno""")
        return self_consump


    def overproduction(self,annual_production:int,self_consumption:int)->int:
        overproduction=int(round(computations.comp_overproduction(annual_production,self_consumption)))
        if overproduction>0:
         st.markdown(f"""- Abbiamo stimato che potresti costuire un impianto che ti farebbe raggiungere {overproduction} kWh/anno di **sovraproduzione** nelle ore centrali della giornata""")
        return overproduction
    
 
    def CO2_reducted(self,energy_self_consum:int|float):
        CO2=int(round(computations.computation_reduced_CO2(energy_self_consum)))
        st.markdown(f"""- Inoltre ridurresti la tua **produzione di CO2** di {CO2} kg CO2/kWh all'anno""")
        return CO2
    
    def enter_or_create_CER(self,benefit:float|int,members:dict):
        filtered_data = {k: v for k, v in members.items() if v > 0}
        result_list = [f"{v} {k}" for k, v in filtered_data.items()]
        result_string = ", ".join(result_list)
        st.markdown(f"""- Valuta la possibilità di entrare a fare parte o creare una **CER**, potresti ricevere fino a **{benefit}€** all'anno di incentivi.
                    I **membri ideali** con cui potresti costituire la CER sono: **{result_string}**""")
                
    def enter_or_create_Group(self,benefit:float|int):
        st.markdown(f"""- Valuta la possibilità di entrare a fare parte o creare un **Gruppo di Autoconsumatori**, potresti ricevere fino a **{benefit}€** all'anno di incentivi""")
       
    def create_Self_consum(self,benefit:float|int):
        st.markdown(f"""- Valuta la possibilità di diventare un **Autoconsumatore a distanza**, potresti ricevere fino a **{benefit}€** all'anno di incentivi""")
                
    def Prosumer_benefit(self,energy_self_consumed:int|float)->int:
        saving=int(round(computations.savings(energy_self_consumed)))
        st.markdown(f"""- Valuta la possibilità di diventare **Prosumer**, potresti risparmiare in bolletta fino a {saving} € in un anno""")
        return saving

            
    def CER_benefit(self,overproduction:int,energy_self_consum:int|float,implant_power:int|float,region:str,comune:str)->Tuple[int|float,dict]:
            CER=CACER_config.CER("CER")
            total_energy=energy_self_consum+overproduction
            benefit=CER.total_benefit(total_energy,implant_power,region,comune)
            members=CER.CER_member(overproduction)
            self.enter_or_create_CER(benefit,members)
            return benefit,members

    def self_consumer_benefit(self,overproduction:int,energy_self_consum:int|float,implant_power:int|float,region:str)->Tuple[int|float]:        
            self_cons=CACER_config.self_consumer("Self consumer")
            benefit=self_cons.benefit_autoconsumed_energy(energy_self_consum,implant_power,region)
            self.create_Self_consum(benefit)
            return benefit 
    
        #depending on the fact that the user has already a PV or only knows the area where to build it, calculated the annual production, implant cost and  PV power 
    def determine_solar_plant_output(self,area_PV:int|None,region:str,annual_consumption:int|float,power:int|float|None)->Tuple[int|float,int|float|None,int|float]:
         if area_PV!=None:
             annual_production,power_peak=self.comput_annual_production_from_area_and_power_peak(area_PV,region)
             implant_cost=self.comput_cost_plant(area_PV)
             power=power_peak
         else:
                annual_production=self.comput_annual_production_from_power(power,region)
                implant_cost=None  
         return annual_production, implant_cost, power
    
#user: "Cittadino"     
class Cittadino_output(User_output):
    def __init__(self, type):
        super().__init__(type)  
       
        
   #depending on the fact that the user area or PV is in the same POD of its house, it is calculated the benefits only as CACER member (not same POD) or as Prosumer and altenratively as CER member(same POD)
   #the fact that the POD is the same or not depends on outcome. 
    def visualize_results_from_same_POD_and_cabin(self,outcome:str,area_PV:int|None,power:int|float|None,region:str,annual_consumption:int|float,comune:str)->Tuple[int,int,int,int|float,int|float,int|float,dict]:     
         annual_production, implant_cost, power=self.determine_solar_plant_output(area_PV,region,annual_consumption,power)
         self_consumption=self.self_consumption(annual_consumption,region,power)
         overproduction=self.overproduction(annual_production,self_consumption) 
         if str(outcome)=="Calculate_cost_and_production":
             benefit,members=self.CER_or_self_consumer_benefit(overproduction,self_consumption,power,region,comune)
             benefit=int(round(benefit))
         if str(outcome)=="Prosumer":
            benefit,members=self.CER_benefit(overproduction,self_consumption,power,region,comune)
            saving=self.Prosumer_benefit(self_consumption)
         return annual_production,power,implant_cost,self_consumption,overproduction,benefit,members
            
    def CER_or_self_consumer_benefit(self,overproduction:int,energy_self_consum:int|float,implant_power:int|float,region:str,comune:str)->Tuple[int|float,dict]:
        if overproduction>0:
            benefit,members=self.CER_benefit(overproduction,energy_self_consum,implant_power,region,comune)
        elif overproduction<=0:
            benefit=self.self_consumer_benefit(overproduction,energy_self_consum,implant_power,region,comune)
            members={}
        return benefit,members
    
    def info_possibility_CER(self):
        st.markdown("- Puoi valutare la possibilità di accedere o costituire una CER. In una CER, se dovessi avere un eccesso di energia prodotta, potresti condividerla con gli altri membri della CER e ricevedere degli incentivi.")
        
    def results_from_user_CACER_choice(self,choice:str,area_PV:int|None,power:int|float|None,region:str,percentage_daily_consump:float,annual_consumption:int|float,comune:str)->Tuple[int,int,int,int|float,int|float,int|float,dict]:     
        annual_production, implant_cost, power=self.determine_solar_plant_output(area_PV,region,annual_consumption,power)
        self_consumption=self.self_consumption(annual_consumption,percentage_daily_consump,annual_production)
        overproduction=self.overproduction(annual_production,self_consumption) 
        members=None
        if choice=="CER":
             benefit,members=self.CER_benefit(overproduction,self_consumption,power,region,comune)
             benefit=int(round(benefit))
             self.CO2_reducted(self_consumption+overproduction)
        elif choice=="Prosumer":
             benefit=self.Prosumer_benefit(self_consumption)
             self.CO2_reducted(self_consumption)
        elif choice=="Autoconsumatore a distanza":
             benefit=self.self_consumer_benefit(overproduction,self_consumption,power,region)
             self.CO2_reducted(self_consumption)
        return annual_production,power,implant_cost,self_consumption,overproduction,benefit,members





