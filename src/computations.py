import pandas as pd
from typing import Dict, Tuple

#mean values of irradiance for each region (kWh/m2)
Irradiance={"Abruzzo":1575,
                    "Basilicata":1603,
                    "Calabria":1677,
                    "Campania":1611,
                    "Emilia-Romagna":1477,
                    "Friuli-Venezia Giulia":1365,
                    "Lazio":1632,
                    "Liguria":1500,
                    "Lombardia":1433,
                    "Marche":1504,
                    "Molise":1568,
                    "Piemonte":1454,
                    "Puglia":1633,
                    "Sardegna":1714,
                    "Sicilia":1786,
                    "Trentino-Alto Adige":1390,
                    "Toscana":1548,
                    "Umbria":1541,
                    "Valle d'Aosta":1502,
                    "Veneto":1424
                    }

# Dati di consumo annuali per tipologia di membri in kWh
consumption_rates: Dict[str, int] = {
    "bar": 8000,  # consumi kWh dalle 10 alle 15 per anno per bar
    "appartamenti": 600,  # consumi kWh dalle 10 alle 15 per anno per cittadino
    "piccolone e medie imprese": 25000,  # consumi kWh dalle 10 alle 15 per anno per PMI
    "hotel": 30000,  # consumi kWh dalle 10 alle 15 per anno per Hotel
    "ristoranti": 10000,  # consumi kWh dalle 10 alle 15 per anno per hotel
}

area_usable_percentage=0.85 #area trurly usable for the PV, excluding the area necessary for the maintenance, shading
loss_factor=0.8 #to take into account losses in the system, such as those due to the inverter, wiring, dust on the panels ecc. It can vary
efficiency=0.2 #efficinecy of PV. It can vary
Power_peak=300 #Wp of one PV
Area_one_PV= 1.6 #area for 1 PV of Power_peak Wp in m2
energy_price=0.25 #0.25 euro/kWh

#COMPUTATION OF ANNUAL PRODUCTION DEPENDING ON REGION (to know the irradiance) AND AVAILABLE AREA 
def computation_annual_production(area_PV:int|float,region:str)->Tuple[float,float]:
    Area_eff=area_usable_percentage*area_PV 
    if region not in Irradiance:
        raise ValueError(f"Regione '{region}' non trovata nel dizionario di irradiance.")
    irradiance = Irradiance[region]
    PV_yield=(Power_peak/1000)/Area_one_PV #kWp/m2
    Energy_year=Area_eff*irradiance*PV_yield*loss_factor #energy in kWh/year formula from https://www.sunbasedata.com/blog/how-to-calculate-solar-panel-output
    P_installable=(Area_eff/Area_one_PV)*Power_peak
    return Energy_year,P_installable

#computation of intallation costs based on installable power
def computation_installation_cost(P_installable:float)->float:
    kW_cost=1000 #cost of PV panels for kW, euro
    installation_cost=kW_cost*P_installable
    return installation_cost

#computation optimal PV dimension based on annual consumption and region (region necessary to know the irradiance)
def computation_optimal_dimension(annual_consumption:int|float,region:str)->int|float:
    efficiency=0.2 #efficiency of PV panel, it can vary
    coverage_score=0.7 #how much of annual consumption must be covered by PV, in general it is suggested to be around 70%
    required_PV_energy=annual_consumption*coverage_score
    if region not in Irradiance:
        raise ValueError(f"Regione '{region}' non trovata nel dizionario di irradiance.")
    PV_dimension=required_PV_energy/(Irradiance[region]*efficiency*loss_factor)
    PV_dimension=PV_dimension/area_usable_percentage #area necessary
    return PV_dimension


##INCENTIVES
  #incentive on self-consumed energy as defined in decreto MASE 07/12/2023
def incentive_self_consumption(energy_self_consum:int|float,implant_power:int|float,region:str)->int|float: #energy and implant power in kWh,kW
   ARERA_valorisation=8 #valorisation of ARERA, it can vary, generally is around 8 euro/MWh. 
   energy_self_consum=energy_self_consum/1000 #conversion in MWh
   #tariff definition
   if implant_power<200:
    tariff=120 + ARERA_valorisation #max of tariff with power <200 KW
   elif implant_power<600:
    tariff=110 + ARERA_valorisation #max of tariff with power <600 KW
   elif implant_power<1000:
    tariff=100 + ARERA_valorisation #max of tariff with power <600 KW
   else:
      tariff=ARERA_valorisation
    #tariff increase depending on the area
   if implant_power<1000: 
    if region in ["Lazio","Marche","Toscana","Umbria","Abruzzo"]:
        tariff=tariff+4 
    elif region in ["Emilia-Romagna","Friuli-Venezia Giulia","Liguria","Lombardia","Piemonte","Veneto","Trentino-Alto Adige","Valle d'Aosta"]:
        tariff=tariff+10
   benefit=tariff*energy_self_consum 
   return int(round(benefit))

#incentive on CER and Groups of self-consumers in municipalities with < 5000 inhabitants
def incentive_municipality(implant_power:int|float)->int|float:#implant power in kW
   if implant_power < 20: #power < 20kW
    benefit=1500*implant_power 
   elif implant_power < 200: #power < 200kW
    benefit=1200*implant_power
   elif implant_power < 600: #power < 600kW
    benefit=1100*implant_power
   else:
    benefit=1050*implant_power #power >600kW
   return int(round(benefit))

#Reduced CO2
def computation_reduced_CO2(energy_self_consum:int|float)->int|float: #energy in kWh
  avg_emissions_factor=  0.309 # how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
  reduced_CO2=energy_self_consum*avg_emissions_factor 
  return reduced_CO2

#saving of Prosumer
def savings(energy_self_consumed:int|float)->int|float:
   savings=energy_self_consumed*energy_price
   return savings

##COMPUTATION OF SELF CONSUMPTION

#the process involves calculating the total annual consumption of an user of example by summing up hourly data (consumption_PV_example.csv), 
#then normalizing example's consumption by dividing each hourly value by this sum. 
#Subsequently, these normalized values are multiplied by the total annual consumption of user to obtain user's consumption predictions for each hour of the day.
def estimate_energy_profile(annual_consum:int|float)->pd.DataFrame:
    df_consumption=pd.read_csv("../resources\consumption_PV_example.csv", delimiter=';')
    # Calculate the total sum of example consumption (for normalization)
    total_example_consum = df_consumption['Consumption'].sum()
   # Normalize example consumption data
    df_consumption['NormalizedConsumption'] = df_consumption['Consumption'] / total_example_consum
    # Scale example normalized data to fit user total annual consumption
    df_consumption['ScaledConsumption'] = df_consumption['NormalizedConsumption'] * annual_consum
    df_hour_year_consumption=df_consumption[['DateUTC', 'ScaledConsumption']]
    return df_hour_year_consumption

#estimate of the production profile of the user's PV plant using as reference the production profile in production_PV_example.csv
def estimate_production_profile(region:str,power_peak:int|float)->pd.DataFrame:
   df_production=pd.read_csv("../resources\production_PV_example.csv", delimiter=';')
   example_annual_irradiance=1575 #annual mean irradiance of the PV plant taken as example
   example_power=1 #considering a PV panel of 1kW power peak
   irradiance=Irradiance[region]
    # normalization example's production data to get an estimate for our PV hourly production in 1 year. 
    # normalization done by multiplying the sample output by the ratio of the real to the sample peak power, 
    # and by the ratio of the real irradiance of the region to the sample one.
   df_production["ScaledProduction"] = df_production["Production"]* (power_peak / example_power) * (irradiance / example_annual_irradiance)
   df_hour_year_production=df_production[['DateUTC',"ScaledProduction"]]
   return df_hour_year_production


def calculation_hourly_self_consumption(df_hour_year_consumption:pd.DataFrame,df_hour_year_production:pd.DataFrame)->pd.DataFrame:
 merged_df = pd.merge(df_hour_year_consumption, df_hour_year_production, on='DateUTC', how='inner')
 #self consumption calculated as min between production and consumption
 merged_df['Houry_self-consumption'] = merged_df[['ScaledConsumption', 'ScaledProduction']].min(axis=1)
 df_hourly_self_consump=merged_df[['DateUTC', 'Houry_self-consumption']]
 return  df_hourly_self_consump


def self_consumption_year(df_hourly_self_consump:pd.DataFrame)->int|float:
   self_consumed_energy_year = df_hourly_self_consump['Houry_self-consumption'].sum()
   return self_consumed_energy_year

def computation_self_consump_and_avg_hour_overproduct(annual_consum:int|float,region:str,power_peak:int|float)->int|float:
   df_hour_year_production=estimate_energy_profile(annual_consum)
   df_hour_year_consumption=estimate_production_profile(region,power_peak)
   df_hourly_self_consump=calculation_hourly_self_consumption(df_hour_year_consumption,df_hour_year_production)
   self_consump=self_consumption_year(df_hourly_self_consump)
   return self_consump

#computation of the average hours in which there is overproduction
def comp_avg_hours_overproduction(df_hour_year_production:pd.DataFrame,df_hour_year_consumption:pd.DataFrame)-> pd.Index:
    df_hour_year_production['DateUTC'] = pd.to_datetime(df_hour_year_production['DateUTC'], dayfirst=True)
    df_hour_year_consumption['DateUTC'] = pd.to_datetime(df_hour_year_consumption['DateUTC'], dayfirst=True)
    df_merged = pd.merge(df_hour_year_production, df_hour_year_consumption, on='DateUTC')
    df_merged['Difference'] = df_merged['ScaledProduction'] - df_merged['ScaledConsumption']
    df_merged['Hour'] = pd.to_datetime(df_merged['DateUTC']).dt.hour
    # group the data by time of day and average the difference
    hourly_average_difference = df_merged.groupby('Hour')['Difference'].mean()
    # identify the hours with overproduction (average of the positive difference)
    hours_with_surplus = hourly_average_difference[hourly_average_difference > 0].index
    print(hours_with_surplus)
    return hours_with_surplus

def hours_overproduction(avg_hours_overproduct:pd.Index)->str:
        day_period={
            0: "di notte",
            1: "di notte",
            2: "di notte",
            3: "di notte",
            4: "di notte",
            5: "di notte",
            6: "di mattina",
            7: "di mattina",
            8: "di mattina",
            9: "di mattina",
            10: "di mattina",
            11: "di mattina",
            12: "nelle ore centrali della giornata",
            13: "nelle ore centrali della giornata",
            14: "nelle ore centrali della giornata",
            15: "nelle ore centrali della giornata",
            16: "di pomeriggio",
            17: "di pomeriggio",
            18: "di pomeriggio",
            19: "di sera",
            20: "di sera",
            21: "di sera",
            22: "di notte",
            23: "di notte"
        }
        # Count occurrences of each part of the day
        counts = {
            "di notte": 0,
            "di mattina": 0,
            "nelle ore centrali della giornata": 0,
            "di pomeriggio": 0,
            "di notte": 0
        }
        for hour in avg_hours_overproduct:
            part_of_the_day = day_period[hour]
            counts[part_of_the_day] += 1
        # Find the part of the day with the majority of occurrences
        predominat_hours_overproduction = max(counts, key=counts.get)
        return predominat_hours_overproduction
   
def avg_overproduction_time(annual_consum:int|float,region:str,power_peak:int|float)->str:
    df_hour_year_production=estimate_energy_profile(annual_consum)
    df_hour_year_consumption=estimate_production_profile(region,power_peak)
    hours_with_surplus=comp_avg_hours_overproduction(df_hour_year_production,df_hour_year_consumption)
    avg_time_overproduction=hours_overproduction(hours_with_surplus)
    return avg_time_overproduction

   
#computation of the fact that there is or not overproduction on average yearly values
def comp_if_there_is_overproduction(production:int|float,self_consumption:int|float)->int|float:
  overproduction = production - self_consumption
  return overproduction

#function that computes the number and typology of members of CER
def find_optimal_members(
    overproduction: int
) -> Dict[str, int]:
    """
    Determina il numero ideale e la tipologia di membri per massimizzare il consumo dell'overproduction.

    :param overproduction: Energia sovraprodotta in kWh
    :param consumption_rates: Dizionario con i consumi annuali in kWh per ogni tipologia di membri
    :return: Dizionario con il numero di membri per ogni tipologia
    """
    members = {key: 0 for key in consumption_rates.keys()}
    remaining_overproduction = overproduction

    # Ordina i membri per consumo decrescente
    sorted_members = sorted(consumption_rates.items(), key=lambda x: x[1], reverse=True)

    for member_type, consumption_rate in sorted_members:
        if remaining_overproduction <= 0:
            break
        num_members = int(remaining_overproduction // consumption_rate)
        members[member_type] = num_members
        remaining_overproduction -= num_members * consumption_rate

    return members



  