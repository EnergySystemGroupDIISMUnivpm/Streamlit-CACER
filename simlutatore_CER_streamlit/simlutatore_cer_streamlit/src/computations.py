import pandas as pd

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

#COMPUTATION OF ANNUAL PRODUCTION DEPENDING ON REGION (to know the irradiance) AND AVAILABLE AREA 
def computation_annual_production(area_PV,region):
    usable_percentage=0.85
    Area_eff=usable_percentage*area_PV #area trurly usable for the PV, excluding the area necessary for the maintenance, shading
    P_m2=150 #considering this power (peak Watt) per square meter.
    P_installable=Area_eff*P_m2
    efficiency=0.85
    if region not in Irradiance:
        raise ValueError(f"Regione '{region}' non trovata nel dizionario di irradiance.")
    irradiance = Irradiance[region]
    Energy_year=P_installable*irradiance*efficiency #energy in kWh/anno

    return Energy_year,P_installable

#computation of intallation costs based on PV area
def computation_installation_cost(area_PV):
    m2_cost=250 #cost of PV panels for m2, euro
    installation_cost=m2_cost*area_PV
    return installation_cost

#computation optimal PV dimension based on annual consumption and region (to know the irradiance)
def computation_optimal_dimension(annual_consumption,region):
    efficiency=0.2 #efficiency of PV panel, it can vary
    coverage_score=0.7 #how much of annual consumption must be covered by PV, in general it is suggested to be around 70%
    required_PV_energy=annual_consumption*coverage_score
    if region not in Irradiance:
        raise ValueError(f"Regione '{region}' non trovata nel dizionario di irradiance.")
    PV_dimension=required_PV_energy/(Irradiance[region]*efficiency)
    return PV_dimension


##INCENTIVES
  #incentive on self-consumed energy (minimum between energy produced by the systems and energy consumed) as defined in decreto MASE 07/12/2023
def incentive_self_consumption(energy_self_consum,implant_power,region): #energy in MWh
   ARERA_valorisation=8 #valorisation of ARERA, it can vary, generally is around 8 euro/MWh. 
   #tariff definition
   if implant_power<200:
    tariff=120 + ARERA_valorisation #max of tariff with power <200 MWh
   elif implant_power<600:
    tariff=110 + ARERA_valorisation #max of tariff with power <600 MWh
   else:
    tariff=100 + ARERA_valorisation #max of tariff with power >600 MWh
    #tariff increase depending on the area
   if region in ["Lazio","Marche","Toscana","Umbria","Abruzzo"]:
    tariff=tariff+4 
   elif region in ["Emilia-Romagna","Friuli-Venezia Giulia","Liguria","Lombardia","Piemonte","Veneto","Trentino-Alto Adige","Valle d'Aosta"]:
    tariff=tariff+10
    benefit=tariff*energy_self_consum 
   return benefit

#incentive on CER and Groups of self-consumers in municipalities with < 5000 inhabitants
def incentive_municipality(implant_power):#implant power in kW
   if implant_power < 20: #power < 20kW
    benefit=1500*implant_power 
   elif implant_power < 200: #power < 200kW
    benefit=1200*implant_power
   elif implant_power < 600: #power < 600kW
    benefit=1100*implant_power
   else:
    benefit=1050*implant_power #power >600kW
   return benefit

#Reduced CO2
def computation_reduced_CO2(energy_self_consum): #energy in kWh
  avg_emissions_factor=  0.309 # how much CO2 is emitted for each kWh produced by the italian traditional electricity grid (kg CO2/kWh)
  reduced_CO2=energy_self_consum*avg_emissions_factor 
  return reduced_CO2


##COMPUTATION OF SELF CONSUMPTION

#the process involves calculating the total annual consumption of A by summing up hourly data, 
#then normalizing A's consumption by dividing each hourly value by this sum. 
#Subsequently, these normalized values are multiplied by the total annual consumption of B to obtain B's consumption predictions for each hour of the day.
def estimate_energy_profile(annual_consum):
    df_consumption=pd.read_csv("../resources\consumption_PV_example.csv", delimiter=';')
    # Calculate the total sum of example consumption (for normalization)
    total_example_consum = df_consumption['Consumption'].sum()
   # Normalize example consumption data
    df_consumption['NormalizedConsumption'] = df_consumption['Consumption'] / total_example_consum
    # Scale example normalized data to fit user total annual consumption
    df_consumption['ScaledConsumption'] = df_consumption['NormalizedConsumption'] * annual_consum
    df_hour_year_consumption=df_consumption[['DateUTC', 'ScaledConsumption']]
    return df_hour_year_consumption

def estimate_production_profile(region,power_peak):
   df_production=pd.read_csv("../resources\production_PV_example.csv", delimiter=';')
   example_annual_irradiance=1575 #annual mean irradiance of the PV panel taken as example
   example_power=1 #considering a PV panel of 1kW power peak
   irradiance=Irradiance[region]
    # normalization example's production data to get an estimate for our PV hourly production in 1 year
   df_production["ScaledProduction"] = df_production["Production"]* power_peak / example_power * irradiance / example_annual_irradiance
   df_hour_year_production=df_production[['DateUTC',"ScaledProduction"]]
   return df_hour_year_production


def calculation_hourly_self_consumption(df_hour_year_consumption,df_hour_year_production):
 merged_df = pd.merge(df_hour_year_consumption, df_hour_year_production, on='DateUTC', how='inner')
 merged_df['Houry_self-consumption'] = merged_df[['ScaledConsumption', 'ScaledProduction']].min(axis=1)
 df_hourly_self_consump=merged_df[['DateUTC', 'Houry_self-consumption']]
 return  df_hourly_self_consump


def self_consumption_year(df_hourly_self_consump):
   self_consumed_energy_year = df_hourly_self_consump['Houry_self-consumption'].sum()
   return self_consumed_energy_year

def computation_self_consump(annual_consum,region,power_peak):
   df_hour_year_production=estimate_energy_profile(annual_consum)
   df_hour_year_consumption=estimate_production_profile(region,power_peak)
   df_hourly_self_consump=calculation_hourly_self_consumption(df_hour_year_consumption,df_hour_year_production)
   self_consump=self_consumption_year(df_hourly_self_consump)
   return self_consump
   
#computation of the fact that there is or not overproduction
def comp_if_there_is_overproduction(production,self_consumption):
  overproduction = production - self_consumption
  return overproduction