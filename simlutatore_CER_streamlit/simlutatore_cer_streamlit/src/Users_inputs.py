import streamlit as st
import datetime
from typing import Tuple

#class with methods common to all users
class User_input:
 def __init__(self, type):
  self.type=type

 def insert_annual_consumption(self)->int:
      annual_consumptiont=st.number_input("Seleziona i tuoi consumi annui", key="consumption", step=1, format="%d", help="Puoi trovare i tuoi consumi annui sulla tua bolletta, kWh")
      return annual_consumptiont
 
 def insert_region(self)->str:
     regions=["Piemonte","Valle d'Aosta", "Lombardia", "Trentino-Alto Adige", "Veneto", "Friuli-Venezia Giulia", "Liguria", "Emilia-Romagna", "Toscana", "Umbria", "Marche", "Lazio", "Abruzzo", "Molise", "Campania", "Puglia", "Basilicata", "Calabria", "Sicilia", "Sardegna"]
     region=st.selectbox("Seleziona la tua regione", regions, index=None)
     return region
 
 def insert_area(self)->int:
    area_PV=st.number_input("Inserisci le dimensioni dell'area in cui costruire l'impianto", key="PV_area_dim", step=1, format="%d")
    return area_PV
 
 def insert_year_power_PV(self)->Tuple[datetime.date,int]:
    year_PV=st.date_input("Inserisci la data di entrata in esercizio dell'impianto PV", format="DD/MM/YYYY", key="PV_year")
    power_PV=st.number_input("Inserisci la potenza dell'impianto PV",step=1, format="%d",key="PV_power")
    return year_PV, power_PV
 
 def want_to_install_PV(self)->str:
    want_PV=st.radio("Vuoi costruire un impianto PV?", options=["Si","No"],index=None, horizontal=True, key="want_PV" )
    return want_PV
 
 def know_where_to_install_PV(self)->str:
    know_where_PV=st.radio("Sai già dove costruire l'impianto?", options=["Si","No"], index=None, horizontal=True,key="know_PV_area" )
    return know_where_PV
 
 def insert_comune(self)->str:
    comune=st.radio("Il comune dove hai l'impianto o dove vuoi costruirlo, ha meno di 5000 abitanti?", options=["Si","No"],index=None, horizontal=True,key="comune_inhabitants")
    return comune
 
 def elaboration_want_or_not_to_install_PV(self,want_PV:str)->Tuple[str|None,int|None]:
      if want_PV=="Si":
             know_where_PV=self.know_where_to_install_PV()
             if know_where_PV=="Si":
              area_PV=self.insert_area()
             else:
                area_PV=None
      else:
             area_PV=None
             know_where_PV=None
      return know_where_PV,area_PV
 
 def presence_or_construction_PV(self)->Tuple[datetime.date|None,int|None,str|None,int|None,str|None]:
     presence_PV_plant=st.radio("Hai già un impianto PV", options=["Si","No"],index=None, horizontal=True, key="presence_PV" )
     if presence_PV_plant=="Si":
        year_PV,power_PV=self.insert_year_power_PV()
        area_PV=None
        know_where_PV=None
        if year_PV < (datetime.datetime.strptime("16/12/2021", "%d/%m/%Y").date()):
           st.markdown("Non è possibile prendere incentivi su questa UP *(DECRETO CACER e TIAD, Regole operative per l’accesso al servizio per l’autoconsumo diffuso e al contributo PNRR, Allegato 1, Parte II, capitolo1, sezione 1.2.1.2.c)*")
           want_PV=self.want_to_install_PV()
           know_where_PV,area_PV=self.elaboration_want_or_not_to_install_PV(want_PV)
     elif presence_PV_plant=="No":
          year_PV=None
          power_PV=None
          want_PV=self.want_to_install_PV()
          know_where_PV,area_PV=self.elaboration_want_or_not_to_install_PV(want_PV)
     else:
        year_PV=None
        power_PV=None
        area_PV=None
        know_where_PV=None
     if presence_PV_plant=="Si" or know_where_PV=="Si":
        comune=self.insert_comune
     else:
        comune=None
     return year_PV,power_PV,know_where_PV,area_PV,comune
 
#user: "Cittadino"
class Cittadino_input (User_input):
 def __init__(self, type):
        super().__init__(type)  
        
 def insert_POD_house(self)->str:  
    same_POD_house=st.radio("L'area dove costruire l'impianto, ha lo stesso POD di casa tua", options=["Si","No"],index=None, horizontal=True, key="POD_area_house" )
    return same_POD_house
      
 def area_same_POD_and_cabin_house(self)->str:
      same_POD_house=self.insert_POD_house()
      if same_POD_house=="No":
       same_Cabina_house=st.radio("L'area dove costruire l'impianto, è nella stessa cabina primaria di casa tua", options=["Si","No"],index=None, horizontal=True, key="cabina_area_house" )
       if same_Cabina_house=="No":
          st.write("Non puoi accedere agli incentivi") #to be defined
          outcome="No_incentives"
          return outcome
       elif same_Cabina_house=="Si":
         outcome="Calculate_cost_and_production"
         st.markdown("<h2 style='text-align: center; color: #0078AC;'>Step 2: Visualizza i risulati nella sezione ✅Risultati </h2>", unsafe_allow_html=True)
         return outcome
      elif same_POD_house=="Si":
       outcome="Prosumer" #to be defined
       return outcome
              
       
 

             

