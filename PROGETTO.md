# PANORAMICA

Voglio creare una mini web game per giocare a CodeName (gioco che segue queste regole https://www.seriamentenerd.it/giochi-da-tavolo/nome-in-codice-guida-completa-al-gioco-base-e-alle-varianti/). Questa mini web app deve essere una docker image eseguibile poi dal piano base di vercel, essendo un progetto personale.

Questa web game mi serve principalmente per fare un'attività di gruppo con degli adolescenti. Siccome il gruppo è numeroso ho bisogno di apportare alcune modifiche al gioco:
1. A differenza della versione standard del gioco che ha solo 2 squadre la mia può avere fino a 5 squadre
2. Il tabellone può essere 5x5 o 5x6
3. il numero di carte per squadra, carte civili e carte assassino è selzionabile all'inizio del gioco. Il numero massimo di carte per squadra sarà quindi automatico in base alla selezione della grandezza del tabellone carte civili assasino ecc. Si possono avere anche zero carte civili

Questa app serve come supporto per giocatori nella stessa stanza con idealmente due dispositivi, tabellone principale proiettato e visualizzazione spymaster per vedere il tabellone con le corrette assegnazioni

# STACK TECNOLOGICO

- Backend: python fastapi
- Frontend: SvelteKit
- DB: SQLLite

Altri tip: usa uv laddove possibile

# FLUSSO LOGICO

- Apertura app fa configurare partita con numero di squadre e relativi nomi e colori
- Impostazioni gioco con griglia e numero carte
- Una volta avviata la partita il backend seleziona le parole e salva su DB le informazioni relative a questa partita. Ogni partita ha associato un identificativo automatico. Questo sarà poi il path url per riaccendere alla partita qual ora si chiuda il browser o si voglia aprire da un altro dispositivo. Id deve essere abbastanza semplice, non un UUID troppo lungo da scrivere
- Si avvia l'app mostrando la griglia delle carte e gli altri elementi UI che mostrano punteggio e il resto delle informazioni utili
- Deve esserci una modalità "SpyMaster" dove le carte del tabellone si colorano in base alla squadra che ha assegnata la carta/carta civile/carta assasino. Questo serve per far sì che gli spymaster possano aprire la partita sul proprio dispoitivo e avere tutto chiaro. Valuta se può aver senso mettere questa schermata dietro una password (salvabile in chiaro nel db) impostabile ad inizio partita
- Nella schermata normale si procede turno per turno (app deve mostrare chiaramente a chi tocca e gestire i cambi turno in base alle regole). Chi ha il controllo della schermata può cliccare sulla carta e una volta confermata con un'animazione si andrà a rivelare la vera assegnazione della carta e di che tipologia sia

# LISTA PAROLE

Crea nel DB una lista di sostantivi italiani (almeno 500) adatti al gioco

# DESIGN

Una uno stile adatto molto spying, che ritorni le vibe del gioco in codice