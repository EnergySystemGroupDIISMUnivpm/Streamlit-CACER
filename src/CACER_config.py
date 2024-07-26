import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)
import computations
from typing import Dict, Tuple
import datetime

#common to all types of CACER
#auconsumatore a distanza
class self_consumer():
    def __init__(self, type):
        self.name = type

    #incentives on self consumed energy
    def benefit_autoconsumed_energy(self,energy_consumed:int|float,implant_power:int|float,implant_year:datetime.date,boosting_power:int,region:str)->int|float:
        benefit_autoconsumed=computations.incentive_self_consumption(energy_consumed,implant_power,implant_year,boosting_power,region)
        return benefit_autoconsumed
    
    #only for groups of self consumers   
class groups_self_consumers(self_consumer):
     def __init__(self, type):
        self.name = type

     #incentives on municipalities with <5000 inhabitants
     def benefit_comune(self,implant_power:int|float)->int|float:
        benefit_municip=computations.incentive_municipality(implant_power)
        return benefit_municip
     
     def total_benefit(self,energy_self_consum:int|float,implant_power:int|float,implant_year:datetime.date,boosting_power:int,region:str,comune:str)->float|int:
         benefit_autoconsumed=self.benefit_autoconsumed_energy(energy_self_consum,implant_power,implant_year,boosting_power,region)
         if comune=="Si":
          benefit_municipality=self.benefit_comune(implant_power)
          benefit=benefit_autoconsumed+benefit_municipality
         else:
             benefit=benefit_autoconsumed
         return benefit
     
     
class CER(groups_self_consumers):
    def __init__(self, type):
        self.name = type
   
    #computation optimal members
    def CER_member(self,overproduction:int|float)-> Dict[str, int]:
        members=computations.find_optimal_members(overproduction)
        return members
        
    
          

    

    
    