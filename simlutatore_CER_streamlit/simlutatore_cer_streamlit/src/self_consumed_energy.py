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


#the process involves calculating the total annual consumption of A by summing up hourly data, 
#then normalizing A's consumption by dividing each hourly value by this sum. 
#Subsequently, these normalized values are multiplied by the total annual consumption of B to obtain B's consumption predictions for each hour of the day.
def estimate_energy_profile(annual_consum):
    df_consumption=pd.read_csv("resources\consumption_PV_example.csv", delimiter=';')
    # Calculate the total sum of example consumption (for normalization)
    total_example_consum = df_consumption['Consumption'].sum()
   # Normalize example consumption data
    df_consumption['NormalizedConsumption'] = df_consumption['Consumption'] / total_example_consum
    # Scale example normalized data to fit user total annual consumption
    df_consumption['ScaledConsumption'] = df_consumption['NormalizedConsumption'] * annual_consum
    df_hour_year_consumption=df_consumption[['DateUTC', 'ScaledConsumption']]
    return df_hour_year_consumption

def estimate_production_profile(region,power_peak):
   df_production=pd.read_csv("resources\production_PV_example.csv", delimiter=';')
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
   


