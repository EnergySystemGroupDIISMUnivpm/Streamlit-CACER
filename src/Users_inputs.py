import streamlit as st
import datetime
from typing import Tuple
import Info_CACER

# class with methods common to all users
class UserInput:
 
     def __init__(self, type):
        self.type = type
        self.PV = True

     def visualize_results(self):
        st.markdown(
            "<h2 style='text-align: center; color: #0078AC;'>Step 2: Visualizza i risulati nella sezione ✅Risultati </h2>",
            unsafe_allow_html=True,
        )

     def insert_annual_consumption(self) -> int:
        annual_consumptiont = st.number_input(
            "Seleziona i tuoi consumi annui in kWh",
            key="consumption",
            step=1,
            format="%d",
            help="Puoi trovare i tuoi consumi annui sulla tua bolletta, kWh",
        )
        return annual_consumptiont

     def insert_region(self) -> str:
        regions = [
            "Piemonte",
            "Valle d'Aosta",
            "Lombardia",
            "Trentino-Alto Adige",
            "Veneto",
            "Friuli-Venezia Giulia",
            "Liguria",
            "Emilia-Romagna",
            "Toscana",
            "Umbria",
            "Marche",
            "Lazio",
            "Abruzzo",
            "Molise",
            "Campania",
            "Puglia",
            "Basilicata",
            "Calabria",
            "Sicilia",
            "Sardegna",
        ]
        region = st.selectbox("Seleziona la tua regione", regions, index=None)
        return region

     def insert_area(self) -> int:
        area_PV = st.number_input(
            "Inserisci le dimensioni dell'area in m² in cui costruire l'impianto",
            key="PV_area_dim",
            step=1,
            format="%d",
        )
        return area_PV

     def insert_year_power_PV(self) -> Tuple[datetime.date, int]:
        year_PV = st.date_input(
            "Inserisci la data di entrata in esercizio dell'impianto PV",
            format="DD/MM/YYYY",
            key="PV_year",
        )
        power_PV = st.number_input(
            "Inserisci la potenza dell'impianto PV in kWh", step=1, format="%d", key="PV_power"
        )
        return year_PV, power_PV

     def want_to_install_PV(self) -> str:
        want_PV = st.radio(
            "Vuoi costruire un impianto PV?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="want_PV",
        )
        if want_PV == "No":
            st.write(
                """
       Siamo spiacenti, ma non puoi ottenere incentivi su un impianto fotovoltaico che non costruisci o potenzi. 
         In alternativa, potresti valutare la possibilità di entrare a far parte di una Comunità Energetica Rinnovabile (CER) o di un gruppo di autoconsumatori, 
         che può portare a benefici significativi in termini ambientali, sociali ed economici. Più nel dettaglio:
         """
            )
            st.subheader("Benefici ambientali:")
            st.markdown(
                """
         - **Riduzione delle emissioni di CO2:** Partecipare a una CER o a un gruppo di autoconsumatori significa contribuire alla produzione e all'utilizzo di energia rinnovabile, riducendo la dipendenza da fonti fossili e abbattendo le emissioni di gas serra.
         - **Promozione della sostenibilità:** Supportando le energie rinnovabili, si favorisce uno sviluppo energetico più sostenibile e rispettoso dell'ambiente.
         """
            )
            st.subheader("Benefici sociali:")
            st.markdown(
                """
         - **Coinvolgimento della comunità:** Le CER e i gruppi di autoconsumatori promuovono la partecipazione attiva dei membri della comunità, rafforzando il senso di appartenenza e la collaborazione tra cittadini.
         - **Educazione e consapevolezza:** Partecipare a una CER o a un gruppo di autoconsumatori può aumentare la consapevolezza sui temi energetici e ambientali, educando i membri della comunità sulle buone pratiche sostenibili.
         """
            )
            st.subheader("Benefici economici:")
            st.markdown(
                """
         - **Riduzione dei costi energetici:** Partecipare a una CER o a un gruppo di autoconsumatori può comportare una riduzione dei costi energetici per i suoi membri grazie all'autoproduzione e all'autoconsumo di energia rinnovabile.
         - **Possibili incentivi e agevolazioni:** Secondo il decreto CACER e TIAD, le CER e i gruppi di autoconsumatori beneficiano di incentivi economici e finanziamenti dedicati alla promozione delle energie rinnovabili.
         """
            )
        return want_PV

     def know_where_to_install_PV(self) -> str:
        know_where_PV = st.radio(
            "Sai già dove costruire l'impianto?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="know_PV_area",
        )
        return know_where_PV

     def want_to_boost_PV(self) -> str:
        want_boost_PV = st.radio(
            "Vuoi potenziare il tuo impianto?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="boosting",
        )
        return want_boost_PV

     def insert_comune(self) -> str:
        comune = st.radio(
            "Il comune dove hai l'impianto o dove vuoi costruirlo, ha meno di 5000 abitanti?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="comune_inhabitants",
        )
        return comune
     
     def insert_boosting_power(self)->int:
         boosting_power=st.number_input(
            "Di quanti kW vuoi potenziare il tuo impianto?", step=1, format="%d", key="boosting_PV_power"
        )
         return boosting_power

     def elaboration_want_or_not_to_install_PV(
        self, want_PV: str
    ) -> Tuple[str | None, int | None]:
        if want_PV == "Si":
            know_where_PV = self.know_where_to_install_PV()
            if know_where_PV == "Si":
                area_PV = self.insert_area()
            else:
                area_PV = None
        else:
            area_PV = None
            know_where_PV = None
        return know_where_PV, area_PV


     def presence_or_construction_PV(
        self,
    ) -> Tuple[
        datetime.date | None, int | None, int, str | None, int | None, str | None, str | None
    ]:
        presence_PV_plant = st.radio(
            "Hai già un impianto PV",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="presence_PV",
        )
        year_PV, power_PV, boosting_power, area_PV, know_where_PV, comune, user_choice = (None, None, 0,None, None, None, None)
        if presence_PV_plant == "Si": #if the user has PV
            year_PV, power_PV = self.insert_year_power_PV()
            comune = self.insert_comune()
            want_boost_PV = self.want_to_boost_PV()
            if want_boost_PV == "Si": #if user want to boost PV
                boosting_power=self.insert_boosting_power()
                user_choice = self.want_to_be_CER_self_Prosumer()
            elif want_boost_PV == "No":
                user_choice = self.want_to_be_CER_self_Prosumer()
        elif presence_PV_plant == "No": #user dosent't have PV
            want_PV = self.want_to_install_PV()
            know_where_PV, area_PV = self.elaboration_want_or_not_to_install_PV(want_PV)
            if know_where_PV == "Si": #if user knows the area 
                comune = self.insert_comune()
                user_choice=self.want_to_be_CER_self_Prosumer()
            elif know_where_PV=="No":
                self.visualize_results()
        return year_PV, power_PV, boosting_power, know_where_PV, area_PV, comune, user_choice
     
     def insert_percentage_daytime_consumption(self)->float:
         daily_consump=st.selectbox(
        "In una giornata tipo, consumi di più di giorno che di notte?", options=["Molto","Mediamente","Poco"], index=None, key="daytime_consump")
         percentage_consump=None
         if daily_consump!=None:   
            percentage_mapping = {
            "Poco": 0.25,
            "Mediamente": 0.50,
            "Molto": 0.75 }
            percentage_consump = percentage_mapping[daily_consump] 
         return percentage_consump

     def want_to_be_CER_self_Prosumer(self):
        choice=st.radio("""Vuoi costituire una CER, essere un Autoconsumatore a distanza o un Prosumer? 
                        Svegli un'opzione.
                        Trovi la spiegazione di ogni opzione qui sotto. """, options=["CER", "Autoconsumatore a distanza", "Prosumer"], key="want_CACER", horizontal=True,index=None)
        
        with st.expander("Visualizza la spiegazione"):
          st.markdown(Info_CACER.info_CER
               )
          st.markdown(Info_CACER.info_Autoconsumatore)
          st.markdown(Info_CACER.info_Prosumer)
          st.markdown(Info_CACER.info_cabine_primarie)
        if choice!=None:
             self.visualize_results()
        return choice

# user: "Cittadino"
class CittadinoInput(UserInput):
    def __init__(self, type):
        super().__init__(type)

    def insert_POD_house(self) -> str:
        same_POD_house = st.radio(
            "L'area dove hai o vuoi costruire l'impianto, ha lo stesso POD di casa tua?",
            options=["Si", "No"],
            index=None,
            horizontal=True,
            key="POD_area_house",
        )
        return same_POD_house

    def area_same_POD_and_cabin_house(self) -> str:
        same_POD_house = self.insert_POD_house()
        if same_POD_house == "No":
            same_Cabina_house = st.radio(
                "L'area dove hai o vuoi costruire l'impianto, è nella stessa cabina primaria di casa tua",
                options=["Si", "No"],
                index=None,
                horizontal=True,
                key="cabina_area_house",
            )
            if same_Cabina_house == "No":
                st.write(
                    "Siamo spiacenti ma non puoi accedere agli incentivi. Secondo il DECRETO CACER e TIAD puoi prendere incentivi solo su PV che sono sotto la stessa cabina primaria dell'utenza"
                )  # to be defined
                outcome = "No_incentives"
                return outcome
            elif same_Cabina_house == "Si":
                outcome = "Calculate_cost_and_production"
                self.visualize_results()
                return outcome
        elif same_POD_house == "Si":
            outcome = "Prosumer"
            self.visualize_results()
            return outcome
