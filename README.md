# Nome in codice

Web game in italiano ispirato a Nome in Codice, per gruppi nella stessa stanza. Da 2 a 5 squadre, tabellone 5×5 o 5×6, conteggi personalizzabili, 988 sostantivi italiani, vista pubblica e mappa Spymaster con protezione facoltativa.

## Stack e struttura

- `frontend/`: SvelteKit 5, compilato come applicazione statica; font inclusi nella build.
- `backend/`: Python + FastAPI. Un Python Worker Cloudflare serve `/api/*`; Workers Static Assets serve il frontend sullo stesso dominio.
- `migrations/`: schema e dizionario di Cloudflare D1. Ogni partita ha uno stato JSON e una revisione. Gli aggiornamenti condizionati alla revisione evitano mosse sovrascritte tra dispositivi.
- Sviluppo rapido: lo stesso backend usa SQLite locale. In Cloudflare usa esclusivamente D1, senza stato di partita in memoria o sul filesystem del Worker.

Non occorre un container Docker per questo deployment. `PROGETTO.md` conserva il brief originale; `PRODUCT.md` contiene le scelte successive concordate.

## Avvio locale rapido

Requisiti: Node.js 22+, npm, uv 0.12.3+ (per Python Workers). uv scarica la versione Python richiesta.

Terminale backend, dalla radice:

```sh
cd backend
uv sync
uv run uvicorn api:app --app-dir src --host 0.0.0.0 --port 8000
```

Terminale frontend:

```sh
cd frontend
npm ci
npm run dev -- --host 0.0.0.0
```

Aprire `http://localhost:5173`. Per il telefono sulla stessa rete usare `http://IP-DEL-PC:5173`; consentire la porta nel firewall se necessario. Vite inoltra le API alla porta 8000.

Il database locale predefinito è `nome-in-codice.sqlite` nella directory temporanea del sistema; impostare `GAME_DB` per conservarlo altrove. Schema e dizionario vengono inizializzati automaticamente in modalità locale.

## Verifica nel runtime Cloudflare locale

Compilare il frontend, poi inizializzare D1 locale:

```sh
cd frontend
npm ci
npm run build
cd ../backend
uv sync
uv run pywrangler d1 migrations apply nome-in-codice --local
uv run pywrangler dev --port 8787
```

Aprire `http://localhost:8787`. Questa modalità prova l'integrazione Python Worker + D1 + asset, senza pubblicare. Il database ID segnaposto nel file di configurazione è sufficiente per D1 locale.

## Pubblicazione su Cloudflare

Occorrono un account Cloudflare e la creazione del database nel proprio account. Nessuna credenziale deve essere inserita nel repository.

```sh
cd backend
uv run pywrangler login
uv run pywrangler d1 create nome-in-codice
```

Copiare il `database_id` restituito in `backend/wrangler.jsonc`, sostituendo il valore tutto zero. Poi:

```sh
uv run pywrangler d1 migrations apply nome-in-codice --remote
cd ../frontend
npm ci
npm run build
cd ../backend
uv run pywrangler deploy
```

Il comando restituisce l'URL pubblico `workers.dev`. Prima del deploy controllare il piano scelto e le quote nel proprio account. Worker e D1 hanno quote gratuite; qui non sono usati Containers o altri servizi a pagamento obbligatori.

## Come giocare

1. Configurare squadre, nomi, colori e carte. Cambiare griglia, civili o assassini ridistribuisce automaticamente gli agenti; i conteggi di ogni squadra restano modificabili. La somma deve essere esattamente 25 o 30. Zero civili e zero assassini sono consentiti.
2. Creare la missione. Il codice pubblico ha 6 caratteri. Il browser dell'organizzatore conserva il permesso di controllo.
3. In **Condividi partita**, copiare il link pubblico e il link Spymaster. Aprire **Mostra accessi riservati** fuori dalla proiezione per ottenere il link di controllo e, se impostato, il codice Spymaster. Conservare il link di controllo per riprendere i comandi da un altro browser: il solo codice partita permette di guardare, non di giocare.
4. Se il codice Spymaster è stato lasciato vuoto, la mappa si apre direttamente a chiunque conosca il link. Se è stato impostato, gli Spymaster devono inserirlo. Gli indizi si danno a voce; l'organizzatore annota indizio e numero sul tabellone.
5. Cliccare una carta e confermare. Tutti i dispositivi aperti si aggiornano ogni 2,5 secondi. Le schede in background sospendono gli aggiornamenti fino al ritorno in primo piano.

### Suggerimenti AI facoltativi

Dopo aver registrato l’indizio, sul tabellone pubblico compare **Chiedi all’AI**. Il pulsante invia in una sola richiesta l’indizio e le parole ancora coperte a `POST https://classifier.dev/v1/classify`, poi mostra quali il classificatore considera possibilmente collegate e quali no. Non invia né riceve le identità delle carte, non rivela carte e non modifica la partita. Dopo una rivelazione o un cambio turno, i suggerimenti precedenti vengono eliminati; premere di nuovo il pulsante per valutare le parole rimaste.

La richiesta parte dal browser che preme il pulsante e usa l’accesso gratuito senza chiave. Il servizio esterno vede l’indizio e le parole inviate. Le risposte sono orientative: associazioni ambigue possono essere classificate male e il risultato può variare tra richieste. Se il servizio non è raggiungibile o applica un limite, il gioco continua normalmente senza suggerimenti. Per un uso più intenso, valutare una chiave workspace e un proxy server-side; non inserire mai una chiave nel frontend. Documentazione: [API](https://classifier.dev/developers), [limiti](https://classifier.dev/pricing).

### Varianti del gruppo

- Prima squadra sorteggiata; nessun agente extra automatico. Con distribuzione non divisibile esattamente, le prime squadre ricevono una carta in più: i conteggi sono visibili e modificabili prima dell'avvio.
- Tentativi pari al numero dell'indizio + 1; indizio 0 per tentativi illimitati. È sempre possibile passare.
- Carta avversaria: conta per l'avversario e termina il turno. Civile: termina il turno.
- Assassino: squadra eliminata. Le sue carte ancora coperte diventano civili; quelle già rivelate mantengono l'identità mostrata.
- Vittoria quando una squadra trova tutti i suoi agenti oppure resta l'unica non eliminata. Dopo la vittoria tutte le identità vengono mostrate.
- Indizio di una sola parola, diverso dalle parole ancora coperte. La validità semantica di derivati, traduzioni e nomi propri resta affidata al gruppo.

### Accessi e conservazione

Le risposte del tabellone pubblico non contengono le assegnazioni delle carte coperte. Il controllo richiede una chiave casuale lunga. La mappa Spymaster è pubblica se non viene impostato un codice; in quel caso chiunque conosca l'URL può vedere le identità. Se è impostato, il server conserva un digest SHA-256 e richiede il codice per leggere la mappa. È un accesso leggero per un gioco in presenza, non un sistema account: non riutilizzare password personali. Nessun recupero dei codici smarriti è previsto.

Se impostato, il codice Spymaster è tenuto solo in memoria sulla sua schermata: dopo una ricarica va reinserito. Il browser dell'organizzatore salva chiave di controllo e l'eventuale codice Spymaster in localStorage. Non condividere il suo profilo browser con i giocatori. D1 conserva le partite finché non vengono eliminate; non è configurata una scadenza automatica.

## Controlli

```sh
cd backend
uv run pytest -q
cd ../frontend
npm run check
npm run build
npx playwright install chromium
# Con API locale :8000 e Vite :5173 già attivi:
node tests/browser-check.mjs
# Oppure il solo Worker locale :8787:
BASE_URL=http://127.0.0.1:8787 node tests/browser-check.mjs
```

Il test browser crea una partita di prova, verifica sincronizzazione da browser separati e salva screenshot in `.impeccable/review/` (ignorati da Git). Usarlo su ambienti locali o di test.

Riferimenti: [Python Workers / FastAPI](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/), [D1](https://developers.cloudflare.com/d1/), [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/).
