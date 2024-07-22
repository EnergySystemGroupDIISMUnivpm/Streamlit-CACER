from typing import Dict, Tuple

# Dati di consumo annuali per tipologia di membri in kWh
CONSUMPTION_RATES: Dict[str, int] = {
    "bar": 8000,  # consumi kWh dalle 10 alle 15 per anno per bar
    "citizen": 600,  # consumi kWh dalle 10 alle 15 per anno per cittadino
    "pmi": 25000,  # consumi kWh dalle 10 alle 15 per anno per PMI
    "hotel": 30000,  # consumi kWh dalle 10 alle 15 per anno per Hotel
    "restaurant": 10000,  # consumi kWh dalle 10 alle 15 per anno per hotel
}


def find_optimal_members(
    overproduction: int, consumption_rates: Dict[str, int]
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


# Esempio di utilizzo
overproduction = 23500  # kWh sovraprodotta per anno

optimal_members = find_optimal_members(overproduction, CONSUMPTION_RATES)
print(
    f"Numero ideale di membri per consumare {overproduction} kWh di sovrapproduzione:"
)
for member_type, num in optimal_members.items():
    print(f"{member_type.capitalize()}: {num}")

