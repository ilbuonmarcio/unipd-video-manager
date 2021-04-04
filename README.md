# UniPD Video Manager

Il progetto nasce dalla necessitá da parte degli studenti di avere le videolezioni anche nell'impossibilitá di una connessione di rete veloce (ma anche per evitare che certi video vadano poi rimossi, vero docenti...?)

Dato che il sistema di eLearning, ad esser di gentil parola, non é il massimo, abbiamo creato due script chiamati `parser.py` e `downloader.py`, che si occupano rispettivamente di ottenere tutti gli url dei video dalla piattaforma (opportunamente spezzettati in file di 10 secondi l'uno, why?) e di scaricare i video dei corsi che ci interessano.

Per utilizzare questo applicativo avrete bisogno di:

- Credenziali di accesso alla piattaforma eLearning dell'Universitá di Padova
- Python 3.8 o superiore
- Chrome/Chromium installato, con relativo `chromedriver` correttamente associato e configurato
- `ffmpeg` per la concatenazione dei token video (sí, la piattaforma di gestione video ha dei barbatrucchi tecnici anti-download)
- Ed altro che mi saró sicuramente dimenticato :)

## Setup

Una volta installato `python` sul vostro sistema, aprite un terminale e installate `virtualenv` con il seguente comando:

    pip install virtualenv

Una volta installato `virtualenv`, dirigetevi nella cartella del progetto e create un virtual environment nel quale installare le dipendenze di questo pacchetto con il seguente comando:

    virtualenv venv

Ed attivatelo opportunamente:

##### Windows:

    ./venv/Scripts/activate

##### Linux/macOS:

    source ./venv/bin/activate

Se vedete a lato una cosa simile a `(venv) PS /path/to/project/` significa che avete creato ed attivato correttamente il virtual environment!

Per l'installazione delle dipendenze basta effettuare il seguente comando:

    pip install -r requirements.txt

Ricordatevi di installare ffmpeg, chrome e chromedriver e rendeteli accessibili nel PATH!

Per ultima cosa, create un file chiamato `.env` nella cartella principale del progetto e inserite due variabili come descritto qui sotto:

    USERNAME=pippo
    PASSWORD=pluto


## Utilizzo

Per ottenere la lista dei video dei corsi, utilizzate il seguente comando dopo aver opportunamente attivato il virtual environment come spiegato qui sopra:

    python parser.py

In caso di errore, probabilmente rieseguendolo nella maggior parte dei casi va via da solo; in caso di problemi persistenti, aprire una pull request *dettagliatissima e minuziosa nei benché minimi dettagli* o non verrá considerata :)

Per scaricare i corsi dei video, invece, eseguire il seguente comando:

    python downloader.py

Ti chiederá di selezionare il numero del corso, inseritelo e premete il tasto Invio: comincerá a scaricare tutti i video inerenti a quel corso, che troverete poi nella cartella `export/NOMECORSO/` con tutti i file con lo stesso nome delle lezioni inserite nella piattaforma di eLearning.

In caso questo download dei video dia errore, la causa principale è perché è passato troppo tempo dall'esecuzione del `parser.py` ed il `downloader.py`, e quindi di conseguenza i link sono scaduti (vi ho giá detto quanto amo questa piattaforma?)

### Bugs

Avete trovato un bug? Aprite una pull request, grazie!

### Collaborators

[Luca Caprara](https://github.com/playhelp999)

### Licenza

Questo software è reso pubblico e licenziato attraverso la cosiddetta MIT License, di cui troverete una copia nella repository di progetto.