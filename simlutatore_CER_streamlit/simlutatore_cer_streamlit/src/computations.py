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

    return Energy_year

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