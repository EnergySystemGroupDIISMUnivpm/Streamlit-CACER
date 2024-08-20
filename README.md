- [ENEA Simulatore CER](#enea-simulatore-cer)
- [Developers](#developers)
  - [Project canvas](#project-canvas)
  - [Extensions](#extensions)
  - [Project Structure](#project-structure)
  - [Come generare .exe da streamlit](#come-generare-exe-da-streamlit)


# ENEA Simulatore CER
Per ENEA, sviluppo di un simulatore sotto forma di eseguibile. L'obiettivo del simulatore è facilitare l'accesso alla creazione di CACER secondo la normativa. Pertanto, deve includere i seguenti casi: CER, gruppo di autoconsumo, autoconsumatore a distanza. Questi tre casi si traducono nei seguenti casi d'uso: comuni, enti pubblici, associazioni, PMI, cittadini, centri commerciali, Real Estate, amministratori di condominio. Il simulatore deve permettere all'utente di selezionare il proprio caso d'uso e di inserire i parametri necessari per conoscere le informazioni necessarie (compreso, ad esempio, il dimensionamento ottimale o il numero ottimale di membri) per ottenere i benefici come CER, gruppo di autoconsumo o autoconsumatore a distanza.



# Developers

## Project canvas

https://excalidraw.com/#room=090e68830f00b40c002d,wNv_GjRBn8Rdex8HrLCSdw

## Extensions

Be sure to install all recommended extensions in order to be on the same page with all the other developers!

## Project Structure

This project has been restructured to mirror an **MVC** style application.

♻️ All existing scripts have been moved to `old` folders inside `models` or `views`.

```bash
cacer_simulator
├── __init__.py
├── models # ✨ NEW
│   ├── __init__.py
│   └── old
│       ├── CACER_config.py
│       ├── computations.py
│       ├── Info_CACER.py
│       ├── parameters.py
│       ├── session_state_variables.py
│       ├── streamlit_pages_configuration.py
│       ├── User_outputs.py
│       └── Users_inputs.py
└── views # ✨ NEW
    ├── __init__.py
    ├── landing_page.py # ✨ NEW
    └── old
        ├── 1_🏠Homepage.py
        └── pages
            ├── 2_✅Risultati.py
            └── 3_❓FAQ.py
```

You can start the new `main.py` using streamlit

```bash
# invoking streamlit directly
streamlit run main.py

# or via stack
./stack run
```

## Come generare .exe da streamlit 
1. Pushare il codice su GitHub e renderlo pubblico.

2. Deployare l'applicazione streamlit su https://share.streamlit.io/. 

3. Download: https://nodejs.org/en

4. Verificare l'installazione da prompt dei comandi (eseguire come amministratore):`node -v`

5. Installare nativefier tramite il seguente comando:
 `npm install -g nativefier`

6. Convertire l'applicazione streamlit in .exe con il seguente comando (streamlit sharing website url va copiato da https://share.streamlit.io/):
 `nativefier --name '<app.exe name>' '<streamlit sharing website url>' --platform <'windows' or 'mac' or 'linux'>`