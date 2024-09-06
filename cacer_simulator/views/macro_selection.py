from enum import StrEnum

import streamlit as st


class MacroGroup(StrEnum):
    GruppoAutoconsumo = "Gruppo Autoconsumo"
    AutoconsumatoreADistanza = "Autoconsumatore a Distanza"
    ComunitaEnergetica = "Comunità Energetica"


def show_macro_group_selector() -> MacroGroup | None:
    macro_groups = [macro_group.value for macro_group in MacroGroup]
    choice = st.selectbox(
        "Seleziona una delle tre possibili configurazioni di CACER",
        macro_groups,
        index=None,
        key="Type CACER selection",
    )
    with st.expander("Hai bisogno di aiuto per scegliere una configurazione?"):
        st.markdown(
            """#### 1. Comunità Energetica (CER)
Una **Comunità Energetica** è costituita da un gruppo di utenti, che possono essere sia consumatori che produttori di energia, i quali condividono l'energia generata da fonti rinnovabili.

**Requisiti:**
- Tutti i membri devono essere collegati alla stessa cabina primaria. Per verificare la cabina primaria, consulta la [mappa interattiva](https://www.gse.it/servizi-per-te/autoconsumo/mappa-interattiva-delle-cabine-primarie).
- La comunità deve essere composta da almeno due membri, ciascuno con un punto di connessione alla rete elettrica distinto.
- Almeno uno dei membri deve possedere o essere intenzionato a installare un impianto fotovoltaico.

#### 2. Autoconsumatore a Distanza
L'**Autoconsumatore a Distanza** è un singolo utente che utilizza l'energia rinnovabile prodotta in un luogo diverso da quello in cui la consuma.

**Requisiti:**
- Deve possedere o voler costruire un impianto fotovoltaico.
- L'impianto deve avere un punto di connessione alla rete elettrica diverso dal punto di prelievo dell'energia.
- Entrambi i punti di connessione (immissione e prelievo) devono essere sotto la stessa cabina primaria. Per verificare la cabina primaria, consulta la [mappa interattiva](https://www.gse.it/servizi-per-te/autoconsumo/mappa-interattiva-delle-cabine-primarie).

#### 3. Gruppo di Autoconsumatori
Un **Gruppo di Autoconsumatori** è composto da almeno due utenti che vivono nello stesso edificio e condividono l'energia prodotta da fonti rinnovabili.

**Requisiti:**
- I membri devono trovarsi nello stesso edificio e sotto la stessa cabina primaria. Per verificare la cabina primaria, consulta la [mappa interattiva](https://www.gse.it/servizi-per-te/autoconsumo/mappa-interattiva-delle-cabine-primarie).
- L’edificio deve già avere un impianto fotovoltaico, o si deve prevederne l’installazione.
"""
        )

    if choice is None:
        return None
    return MacroGroup(choice)
