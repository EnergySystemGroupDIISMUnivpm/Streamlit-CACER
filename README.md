# ENEA Simulatore CER
Per ENEA, sviluppo di un simulatore sotto forma di eseguibile. L'obiettivo del simulatore è facilitare l'accesso alla creazione di CACER secondo la normativa. Pertanto, deve includere i seguenti casi: CER, gruppo di autoconsumo, autoconsumatore a distanza. Questi tre casi si traducono nei seguenti casi d'uso: comuni, enti pubblici, associazioni, PMI, cittadini, centri commerciali, Real Estate, amministratori di condominio. Il simulatore deve permettere all'utente di selezionare il proprio caso d'uso e di inserire i parametri necessari per conoscere le informazioni necessarie (compreso, ad esempio, il dimensionamento ottimale o il numero ottimale di membri) per ottenere i benefici come CER, gruppo di autoconsumo o autoconsumatore a distanza.


## Come generare .exe da streamlit 
1. Pushare il codice su GitHub e renderlo pubblico.

2. Deployare l'applicazione streamlit su https://share.streamlit.io/. 

3. Download: https://nodejs.org/en

4. Verificare l'installazione da prompt dei comandi (eseguire come amministratore):`node -v`

5. Installare nativefier tramite il seguente comando:
 `npm install -g nativefier`

6. Convertire l'applicazione streamlit in .exe con il seguente comando (streamlit sharing website url va copiato da https://share.streamlit.io/):
 `nativefier --name '<app.exe name>' '<streamlit sharing website url>' --platform <'windows' or 'mac' or 'linux'>`
