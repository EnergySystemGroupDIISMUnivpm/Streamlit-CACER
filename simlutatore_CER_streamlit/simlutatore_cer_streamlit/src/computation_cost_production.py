#COMPUTATION OF ANNUAL PRODUCTION DEPENDING ON REGION AND AVAILABLE AREA 
def computation_annual_production(area_PV,region):
    usable_percentage=0.85
    Area_eff=usable_percentage*area_PV #area trurly usable for the PV, excluding the area necessary for the maintenance, shading
    P_m2=150 #considering this power (peak Watt) per square meter.
    P_installable=Area_eff*P_m2
    efficiency=0.85
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
    if region not in Irradiance:
        raise ValueError(f"Regione '{region}' non trovata nel dizionario di irradiance.")
    irradiance = Irradiance[region]
    Energy_year=P_installable*irradiance*efficiency #energy in kWh/anno

    return Energy_year

