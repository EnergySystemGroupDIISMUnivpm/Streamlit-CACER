from enum import StrEnum

import streamlit as st


class MacroSelection(StrEnum):
    CACER = "CACER"
    Multivettore = "Multivettore energetico"


def homepage() -> MacroSelection | None:
    st.set_page_config(page_icon=":sun_small_cloud:", layout="wide")
    contribution = (
        "Piattaforma finanziata a valere sul Fondo per la ricerca di sistema elettrico"
    )
    st.markdown(
        f"""
    <div style="text-align: right; font-size: 10px;">
        <em>{contribution}</em>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.write(" ")
    col1_title, col2_title, col3_title = st.columns([2, 6, 2])

    with col1_title:
        st.image("./resources/logo_ENEA.png", use_container_width=True)

    with col2_title:
        st.markdown(
            """<h1 style='text-align: center; font-size: 60px;'>Benvenuto in SIMBA</h1>
    <p style='text-align: center; font-size: 22px;'>
    <span style='font-weight: 900;'>S</span>imulator for CACER 
    <span style='font-weight: 900;'>I</span>ntegration & 
    <span style='font-weight: 900;'>M</span>ulti-Energy 
    <span style='font-weight: 900;'>B</span>est 
    <span style='font-weight: 900;'>A</span>ssessment
    </p>""",
            unsafe_allow_html=True,
        )

    with col3_title:
        st.image("./resources/logo_UNIVPM.png", use_container_width=True)

    col1, col2 = st.columns(2)

    # Usare session_state per memorizzare la selezione
    if "selection" not in st.session_state:
        st.session_state["selection"] = None

    # Sezione CACER
    with col1:
        st.header("Sezione CACER")
        st.markdown(
            """
Questo servizio ti consente di simulare scenari di autoconsumo collettivo con energie rinnovabili  aiutandoti a comprendere l'impatto ambientale ed economico delle tue scelte energetiche.

Le **CACER** (Configurazioni di Autoconsumo Collettivo per l'Energia Rinnovabile) sono soluzioni che permettono la condivisione dell'energia elettrica generata da fonti rinnovabili tra più utenti, ottimizzando l'uso delle risorse e riducendo l'impatto ambientale. Utilizzano la rete elettrica esistente per distribuire l'energia prodotta in modo efficiente, con l'obiettivo di ridurre le emissioni di gas serra e offrire benefici economici agli utenti.

Esistono tre configurazioni principali per partecipare a un sistema di autoconsumo collettivo: **Comunità Energetica Rinnovabile (CER)**, **Autoconsumatore a distanza**, **Gruppo di autoconsumatori**.

"""
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
        if st.button("Avvia il Simulatore CACER"):
            st.session_state["selection"] = MacroSelection.CACER

    # Sezione Multivettore energetico
    with col2:
        st.header("Sezione Multivettore energetico")
        st.markdown(
            """
            Questo servizio ti consente di **ottimizzare l'integrazione di diverse fonti energetiche** tramite modelli di multivettori energetici, offrendoti una chiara comprensione dell'impatto economico delle tue decisioni energetiche.
            
            Un multivettore energetico è un sistema che integra diverse fonti di energia, come fotovoltaico, cogenerazione e sistemi di accumulo per ottimizzare l'efficienza complessiva e ridurre le emissioni. A partire dai tuoi consumi elettrici, termici e frigoriferi, il sistema propone le soluzioni energetiche più adatte a te massimizzando l'uso dell'energia disponibile, migliorando la sostenibilità e riducendo significativamente i costi."""
        )
        if st.button("Avvia il Simulatore Multivettore"):
            st.session_state["selection"] = MacroSelection.Multivettore

    return st.session_state["selection"]
