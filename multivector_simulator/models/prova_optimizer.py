# PROVA DI OTTIMIZZAZIONE DI UN SISTEMA MULTIVETTORE.
# FONTI DI ENERGIA: Fotovoltaico (produzione elettrica), idrogeno (produzione calore), rete elettrica, batteria, pompa di calore (produzione calore).
# VINCOLI: impianti fotovoltaici < 1MW ; Impianti di cogenerazione se i consumi sono >25.000kWh all’anno e coprono almeno l’80% delle ore dell’anno.
# SCOPO OTTIMIZZAZIONE: Massimizzare la copertura del fabbisogno , minimizzare l’eccesso di energia.


import pulp
import numpy as np

# Dati di esempio: consumi orari (kWh) per un anno (8760 ore)
ore_totali = 8760  # Numero di ore in un anno
consumi_elettrici = np.random.uniform(0, 10.0, ore_totali)  # Consumi elettrici (kWh)
consumi_termici = np.random.uniform(0, 6.0, ore_totali)  # Consumi termici (kWh)

# Parametri idrogeno e pompa di calore
efficienza_elettrica_h2 = (
    0.5  # Efficienza del sistema a idrogeno per produrre energia elettrica
)
efficienza_termica_h2 = 0.8  # Efficienza del sistema a idrogeno per produrre calore
COP_pompa_calore = 3.0  # Coefficiente di prestazione della pompa di calore

# Energia disponibile dal fotovoltaico per ogni ora (ipotetica, dipende dalla potenza PV installata)
energia_fotovoltaico_base = np.random.uniform(
    0.0, 6.0, ore_totali
)  # Energia disponibile per kWp installato

# Creazione del problema di ottimizzazione
prob = pulp.LpProblem("Ottimizzazione_Massimizzare_Copertura", pulp.LpMaximize)

# Variabili di decisione: grandezze ottimali di batteria, sistema a idrogeno, impianto fotovoltaico e pompa di calore
capacita_batteria_ottima = pulp.LpVariable("capacita_batteria_ottima", lowBound=0)
capacita_idrogeno_ottima = pulp.LpVariable("capacita_idrogeno_ottima", lowBound=0)
potenza_pv_ottima = pulp.LpVariable(
    "potenza_pv_ottima", lowBound=0, upBound=999
)  # Fotovoltaico < 1 MW
capacita_pompa_calore_ottima = pulp.LpVariable(
    "capacita_pompa_calore_ottima", lowBound=0
)  # Dimensionamento pompa di calore

# Variabili di utilizzo orario per ogni fonte di energia
energy_from_grid = pulp.LpVariable.dicts(
    "energy_from_grid", range(ore_totali), lowBound=0
)
energy_from_battery = pulp.LpVariable.dicts(
    "energy_from_battery", range(ore_totali), lowBound=0
)
energy_from_solar = pulp.LpVariable.dicts(
    "energy_from_solar", range(ore_totali), lowBound=0
)
energy_from_hydrogen_electric = pulp.LpVariable.dicts(
    "energy_from_hydrogen_electric", range(ore_totali), lowBound=0
)
energy_from_hydrogen_heat = pulp.LpVariable.dicts(
    "energy_from_hydrogen_heat", range(ore_totali), lowBound=0
)

# Variabili per la pompa di calore
energy_to_heat_pump = pulp.LpVariable.dicts(
    "energy_to_heat_pump", range(ore_totali), lowBound=0
)  # Energia elettrica usata dalla pompa di calore
heat_from_heat_pump = pulp.LpVariable.dicts(
    "heat_from_heat_pump", range(ore_totali), lowBound=0
)  # Calore prodotto dalla pompa di calore

# Variabili per immagazzinare energia
energy_stored_in_battery = pulp.LpVariable.dicts(
    "energy_stored_in_battery", range(ore_totali), lowBound=0
)
hydrogen_produced = pulp.LpVariable.dicts(
    "hydrogen_produced", range(ore_totali), lowBound=0
)
hydrogen_stored = pulp.LpVariable.dicts(
    "hydrogen_stored", range(ore_totali), lowBound=0
)

# Variabile per rappresentare l'energia in eccesso (non utilizzata o non immagazzinabile)
excess_energy = pulp.LpVariable.dicts("excess_energy", range(ore_totali), lowBound=0)

# Variabile binaria per determinare se si usa la cogenerazione
use_cogeneration = pulp.LpVariable("use_cogeneration", cat="Binary")

# Funzione obiettivo: massimizzare la copertura dei consumi minimizzando l'energia in eccesso
prob += (
    pulp.lpSum(
        [
            energy_from_solar[t]
            + energy_from_battery[t]
            + energy_from_grid[t]
            + energy_from_hydrogen_electric[t]
            + heat_from_heat_pump[t]
            - excess_energy[t]
            for t in range(ore_totali)
        ]
    )
), "Massimizzare_Copertura"

# Vincoli per ogni ora
for t in range(ore_totali):
    # Consumo elettrico totale per ogni ora
    consumo_elettrico = consumi_elettrici[t]
    consumo_termico = consumi_termici[t]

    # Vincolo: la somma delle fonti di energia elettrica deve soddisfare i consumi elettrici e la pompa di calore
    prob += (
        energy_from_grid[t]
        + energy_from_battery[t]
        + energy_from_solar[t]
        + energy_from_hydrogen_electric[t]
        >= consumo_elettrico + energy_to_heat_pump[t]
    ), f"Vincolo_Consumi_Elettrici_{t}"

    # Vincolo: la somma delle fonti di calore (idrogeno e pompa di calore) deve soddisfare i consumi termici
    prob += (
        energy_from_hydrogen_heat[t] + heat_from_heat_pump[t] >= consumo_termico
    ), f"Vincolo_Consumi_Termici_{t}"

    # Vincolo: energia solare disponibile è proporzionale alla potenza installata del PV
    prob += (
        energy_from_solar[t] <= potenza_pv_ottima * energia_fotovoltaico_base[t],
        f"Vincolo_Fotovoltaico_{t}",
    )

    # Vincolo: calore prodotto dalla pompa di calore è proporzionale all'energia elettrica usata, limitato dalla capacità della pompa di calore
    prob += (
        heat_from_heat_pump[t] == COP_pompa_calore * energy_to_heat_pump[t],
        f"Vincolo_Pompa_Calore_{t}",
    )
    prob += (
        energy_to_heat_pump[t] <= capacita_pompa_calore_ottima,
        f"Capacita_Pompa_Calore_{t}",
    )

    # Vincolo: gestione delle batterie (energia immagazzinata = immessa meno prelevata)
    if t == 0:
        prob += (
            energy_stored_in_battery[t] == 0
        )  # Supponiamo che all'inizio la batteria sia vuota
    else:
        prob += (
            energy_stored_in_battery[t]
            == energy_stored_in_battery[t - 1]
            + energy_from_solar[t - 1]
            - energy_from_battery[t],
            f"Vincolo_Batterie_{t}",
        )

    # Vincolo: gestione idrogeno (produzione e utilizzo)
    if t == 0:
        prob += (
            hydrogen_stored[t] == 0
        )  # Supponiamo che all'inizio non ci sia idrogeno immagazzinato
    else:
        prob += (
            hydrogen_stored[t]
            == hydrogen_stored[t - 1]
            + hydrogen_produced[t - 1]
            - (
                energy_from_hydrogen_electric[t] * (1 / efficienza_elettrica_h2)
                + energy_from_hydrogen_heat[t] * (1 / efficienza_termica_h2)
            ),
            f"Vincolo_Idrogeno_{t}",
        )

    # Vincolo: energia immagazzinata non può superare la capacità della batteria e dell'idrogeno
    prob += (
        energy_stored_in_battery[t] <= capacita_batteria_ottima,
        f"Capacita_Batterie_{t}",
    )
    prob += hydrogen_stored[t] <= capacita_idrogeno_ottima, f"Capacita_Idrogeno_{t}"

    # Vincolo sull'energia in eccesso: deve corrispondere all'energia prodotta che non può essere utilizzata o immagazzinata
    prob += (
        energy_from_solar[t]
        + energy_from_grid[t]
        + energy_from_battery[t]
        - consumo_elettrico
        + hydrogen_produced[t]
        - (energy_from_hydrogen_electric[t] + energy_from_hydrogen_heat[t])
        >= excess_energy[t]
    ), f"Vincolo_Eccesso_Energia_{t}"

# Aggiunta dei vincoli per l'impianto di cogenerazione
total_consumption = pulp.lpSum([consumi_elettrici[t] for t in range(ore_totali)])
total_cogeneration_usage = pulp.lpSum(
    [energy_from_hydrogen_electric[t] for t in range(ore_totali)]
)

# Vincolo: l'impianto di cogenerazione può essere usato solo se i consumi superano i 25.000 kWh all'anno
prob += total_consumption >= 25000 * use_cogeneration, "Vincolo_Consumi_Cogenerazione"

# Vincolo: l'impianto di cogenerazione deve essere usato almeno nell'80% delle ore dell'anno
prob += (
    total_cogeneration_usage >= 0.8 * ore_totali * use_cogeneration,
    "Vincolo_Ore_Cogenerazione",
)

# Risolvi il problema
prob.solve()

# Output: dimensioni ottimali del sistema
print(f"Capacità ottimale della batteria: {capacita_batteria_ottima.varValue:.2f} kWh")
print(
    f"Capacità ottimale del sistema a idrogeno: {capacita_idrogeno_ottima.varValue:.2f} kg"
)
print(
    f"Potenza ottimale dell'impianto fotovoltaico: {potenza_pv_ottima.varValue:.2f} kWp"
)
print(
    f"Capacità ottimale della pompa di calore: {capacita_pompa_calore_ottima.varValue:.2f} kW"
)
