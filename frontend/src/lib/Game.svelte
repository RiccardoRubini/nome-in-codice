<script>
  import { onMount } from 'svelte';
  import { api, storage } from './api';
  import { classifyClue } from './classifier';
  import Icon from './Icon.svelte';
  let { id, spy = false } = $props();
  let game = $state(null),
    hostKey = $state(''),
    spyCode = $state(''),
    enteredCode = $state('');
  let error = $state(''),
    busy = $state(false),
    connected = $state(true),
    loading = $state(true),
    missing = $state(false);
  let showSharing = $state(false),
    message = $state(''),
    clueWord = $state(''),
    clueNumber = $state(1);
  let selected = $state(null),
    confirmDialog,
    rulesDialog,
    passDialog;
  let lastRevealed = $state(-1),
    authenticated = $state(false),
    requiresCode = $state(false),
    selectedRevision = $state(null),
    passRevision = $state(null),
    destroyed = false,
    timer;
  let aiResult = $state(null),
    aiOpen = $state(false),
    aiLoading = $state(false),
    aiError = $state(''),
    aiController;
  let active = $derived(game?.teams[game.active]);
  let canControl = $derived(!!hostKey && !spy && game?.status === 'playing');
  let aiKey = $derived(
    game?.clue
      ? `${game.turn}|${game.clue.word}|${game.cards.map((card) => (card.revealed ? '1' : '0')).join('')}`
      : ''
  );
  let aiCurrent = $derived(!!aiResult && aiResult.key === aiKey);
  let aiRelated = $derived(
    aiCurrent ? aiResult.items.filter((item) => item.related) : []
  );
  let aiSuggested = $derived(new Set(aiRelated.map((item) => item.index)));
  let origin = $state('');
  let accessCode = $state('');
  const ownerName = (card) =>
    typeof card.owner === 'number'
      ? game.teams[card.owner].name
      : card.owner === 'assassin'
        ? 'Assassino'
        : card.owner === 'civilian'
          ? 'Civile'
          : 'Identità segreta';
  const ownerColor = (card) =>
    typeof card.owner === 'number'
      ? game.teams[card.owner].color
      : card.owner === 'assassin'
        ? '#222c25'
        : '#dadbce';
  function clearAi() {
    aiController?.abort();
    aiController = null;
    aiResult = null;
    aiOpen = false;
    aiLoading = false;
    aiError = '';
  }
  async function suggest() {
    if (aiCurrent) {
      aiOpen = !aiOpen;
      return;
    }
    if (aiLoading || !game?.clue || !connected) return;
    const key = aiKey;
    const candidates = game.cards.flatMap((card, index) =>
      card.revealed ? [] : [{ index, word: card.word }]
    );
    const controller = new AbortController();
    aiController = controller;
    aiLoading = true;
    aiError = '';
    try {
      const items = await classifyClue(game.clue.word, candidates, controller.signal);
      if (aiKey === key) {
        aiResult = { key, items };
        aiOpen = true;
      }
    } catch (error) {
      if (error.name !== 'AbortError') aiError = error.message;
    } finally {
      if (aiController === controller) {
        aiLoading = false;
        aiController = null;
      }
    }
  }
  async function refresh(initial = false) {
    try {
      const suffix = spy ? '/spy' : '';
      const data = await api(`/games/${id}${suffix}`, {
        headers: spy && spyCode ? { 'X-Spy-Code': spyCode } : {}
      });
      if (!game || data.revision >= game.revision) {
        if (game && data.revision > game.revision) {
          clearAi();
          if (confirmDialog?.open) confirmDialog.close();
          if (passDialog?.open) passDialog.close();
          selectedRevision = null;
          passRevision = null;
          if (data.turn !== game.turn) clueWord = '';
        }
        game = data;
      }
      authenticated = true;
      requiresCode = false;
      connected = true;
      missing = false;
      if (initial) error = '';
    } catch (e) {
      connected = false;
      if (e.status === 403 && spy) {
        authenticated = false;
        requiresCode = true;
        spyCode = '';
        error = enteredCode ? 'Codice Spymaster non valido. Riprova.' : '';
      } else if (e.status === 404) {
        missing = true;
        error = e.message;
      } else if (initial) error = e.message;
    } finally {
      loading = false;
    }
  }
  onMount(() => {
    origin = location.origin;
    const hash = new URLSearchParams(location.hash.slice(1));
    const supplied = hash.get('host');
    if (supplied && !spy) {
      storage.set(`host:${id}`, supplied);
      history.replaceState(null, '', location.pathname);
    }
    accessCode = storage.get(`spy:${id}`);
    async function init() {
      const key = storage.get(`host:${id}`);
      if (key && !spy) {
        try {
          await api(`/games/${id}/control`, { headers: { 'X-Host-Key': key } });
          hostKey = key;
        } catch {
          hostKey = '';
        }
      }
      await refresh(true);
      const poll = async () => {
        if (destroyed) return;
        if (!document.hidden && !busy && !(spy && requiresCode && !spyCode))
          await refresh();
        if (!destroyed) timer = setTimeout(poll, 2500);
      };
      if (!destroyed) timer = setTimeout(poll, 2500);
    }
    init();
    return () => {
      destroyed = true;
      clearTimeout(timer);
      aiController?.abort();
    };
  });
  async function login() {
    if (busy) return;
    busy = true;
    spyCode = enteredCode.trim();
    await refresh(true);
    busy = false;
  }
  async function command(values) {
    if (busy || !game || !connected) return;
    busy = true;
    error = '';
    try {
      const data = await api(`/games/${id}/actions`, {
        method: 'POST',
        headers: { 'X-Host-Key': hostKey },
        body: JSON.stringify({
          ...values,
          revision: values.revision ?? game.revision
        })
      });
      game = data;
      clearAi();
      if (values.kind === 'reveal') lastRevealed = values.card;
      if (values.kind === 'clue') clueWord = '';
      selected = null;
      confirmDialog?.close();
      passDialog?.close();
    } catch (e) {
      error = e.message;
      await refresh();
    } finally {
      busy = false;
    }
  }
  function select(index) {
    if (!canControl || !game.clue || !connected || busy) return;
    selected = index;
    selectedRevision = game.revision;
    confirmDialog.showModal();
  }
  async function copy(value, label) {
    try {
      await navigator.clipboard.writeText(value);
      message = `${label} copiato.`;
    } catch {
      message = 'Copia il testo dal campo del link.';
    }
  }
  async function fullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      message =
        'La modalità schermo intero non è disponibile in questo browser.';
    }
  }
  function describe(event) {
    if (event.kind === 'clue')
      return `Indizio: ${event.word} · ${event.number === 0 ? 'illimitati' : event.number}`;
    if (event.kind === 'pass') return 'Turno passato';
    return `${event.word} — ${typeof event.owner === 'number' ? game.teams[event.owner].name : event.owner === 'assassin' ? 'Assassino' : 'Civile'}`;
  }
</script>

<svelte:head
  ><title>{spy ? 'Spymaster' : 'Partita'} {id} — Nome in codice</title><meta
    name="robots"
    content="noindex,nofollow"
  /></svelte:head
>
<header class="masthead game-header">
  <a class="brand" href="/"
    ><Icon name="shield" size={27} /><span>NOME IN CODICE</span></a
  >
  <div class="mission-id"><span>Missione</span><strong>{id}</strong></div>
  <nav aria-label="Azioni partita">
    <button class="quiet" onclick={() => rulesDialog.showModal()}>Regole</button
    >{#if !spy}<a
        class="quiet"
        href={`/g/${id}/spy`}
        target="_blank"
        rel="noopener"><Icon name="eye" /><span>Spymaster</span></a
      >{:else}<a class="quiet" href={`/g/${id}`}>Tabellone pubblico</a
      >{/if}<button
      class="icon-button desktop-only"
      title="Schermo intero"
      aria-label="Schermo intero"
      onclick={fullscreen}><Icon name="expand" /></button
    >
  </nav>
</header>
<main class="game-shell">
  {#if loading}<div class="waiting">
      <h1>Prepariamo il tavolo.</h1>
      <p>Recupero della missione {id}…</p>
    </div>
  {:else if spy && requiresCode && !authenticated && !missing}
    <div class="spy-login">
      <div class="login-emblem"><Icon name="lock" size={40} /></div>
      <h1>Solo per gli<br />Spymaster.</h1>
      <p>
        Qui si vedono tutte le identità.<br />Chiedi il codice segreto a chi ha
        creato la partita.
      </p>
      <form
        onsubmit={(e) => {
          e.preventDefault();
          login();
        }}
      >
        <label for="spy-login">Codice Spymaster</label><input
          id="spy-login"
          type="password"
          bind:value={enteredCode}
          autocomplete="current-password"
          required
        /><button class="primary" disabled={busy || !enteredCode}
          >{busy ? 'Verifica…' : 'Apri la mappa segreta'}<Icon
            name="arrow"
          /></button
        >
      </form>
      {#if error}<p class="error-message" role="alert">{error}</p>{/if}
    </div>
  {:else if !game}<div class="waiting">
      <h1>{missing ? 'Missione non trovata.' : 'Collegamento interrotto.'}</h1>
      <p role="alert">{error}</p>
      <button class="primary" onclick={() => refresh(true)}>Riprova</button><a
        class="quiet"
        href="/">Torna alla preparazione</a
      >
    </div>
  {:else}
    {#if spy}<div class="spy-notice">
        <Icon name="eye" /><strong>Mappa segreta</strong><span
          >Non proiettare questa schermata. Le carte segnate sono già state
          rivelate.</span
        >
      </div>{/if}
    <div class="scoreboard" aria-label="Squadre e agenti rimasti">
      {#each game.teams as team, i}<div
          class="score"
          class:active={i === game.active && game.status === 'playing'}
          class:eliminated={team.eliminated}
          style:--team={team.color}
        >
          <span class="team-letter">{String.fromCharCode(65 + i)}</span>
          <div class="score-name">
            <strong>{team.name}</strong><span
              >{team.eliminated
                ? 'Eliminata'
                : game.winner === i
                  ? 'Missione compiuta'
                  : i === game.active && game.status === 'playing'
                    ? 'In azione'
                    : 'Agenti rimasti'}</span
            >
          </div>
          <span class="score-number"
            >{team.eliminated ? '—' : team.remaining}<small>/{team.total}</small
            ></span
          >
        </div>{/each}
    </div>
    <div class="turn-bar" aria-live="polite">
      <div>
        {#if game.status === 'finished'}<h1>
            Vince {game.teams[game.winner].name}.
          </h1>
          <span class="turn-index">MISSIONE CONCLUSA</span>{:else}<h1>
            Tocca a <span style:color={active.color}>{active.name}.</span>
          </h1>
          <span class="turn-index">TURNO {game.turn}</span>{/if}
      </div>
      <div class="clue-display">
        {#if game.clue}<span>INDIZIO</span><strong
            >{game.clue.word}
            <b>{game.clue.number === 0 ? '∞' : game.clue.number}</b></strong
          ><small
            >{game.guesses_left === null
              ? 'Tentativi illimitati'
              : `${game.guesses_left} tentativi disponibili`}</small
          >{:else if game.status === 'playing'}<span
            >IN ATTESA DELL’INDIZIO</span
          >
          <p>
            {canControl
              ? 'Ascolta lo Spymaster e annota il suo indizio.'
              : 'Lo Spymaster sta preparando la prossima mossa.'}
          </p>{:else}<a class="primary" href="/"
            >Nuova missione <Icon name="arrow" /></a
          >{/if}
      </div>
    </div>
    {#if !connected}<div class="error-message" role="status">
        Collegamento interrotto. Il tabellone si aggiornerà appena torna la
        rete; le azioni sono sospese. <button
          class="text-button"
          onclick={() => refresh(true)}>Riprova</button
        >
      </div>{/if}
    {#if error}<p class="error-message" role="alert">{error}</p>{/if}
    <div
      class="word-board"
      class:six-rows={game.size === 30}
      aria-label={spy ? 'Mappa delle identità' : 'Tabellone delle parole'}
    >
      {#each game.cards as card, i}
        {@const visible = card.owner !== undefined}
        <button
          class="word-card"
          class:revealed={card.revealed}
          class:identity-visible={visible}
          class:civilian={card.owner === 'civilian'}
          class:assassin={card.owner === 'assassin'}
          class:just-revealed={lastRevealed === i}
          class:ai-suggested={aiCurrent && aiOpen && aiSuggested.has(i)}
          style:--team={ownerColor(card)}
          disabled={spy ||
            card.revealed ||
            !canControl ||
            !game.clue ||
            busy ||
            !connected}
          aria-label={`${card.word}${visible ? `, ${ownerName(card)}` : ''}${card.revealed ? ', rivelata' : ''}${aiCurrent && aiOpen && aiSuggested.has(i) ? ', suggerita dall’AI' : ''}`}
          onclick={() => select(i)}
          ><span class="card-index">{String(i + 1).padStart(2, '0')}</span
          >{#if aiCurrent && aiOpen && aiSuggested.has(i)}<span
              class="ai-card-mark"
              aria-hidden="true">AI</span
            >{/if}
          <strong
            lang="it"
            class:long-word={card.word.length >= 9}
            style:--word-length={card.word.length}>{card.word}</strong
          ><span class="card-owner"
            >{#if visible}{card.revealed ? 'RIVELATA · ' : ''}{ownerName(
                card
              )}{:else}IDENTITÀ RISERVATA{/if}</span
          >{#if card.revealed}<span class="revealed-check"
              ><Icon name="check" size={16} /></span
            >{/if}</button
        >
      {/each}
    </div>
    {#if !spy && game.clue && game.status === 'playing'}
      <section class="ai-assist" aria-label="Suggerimenti AI">
        <div class="ai-assist-intro">
          <div>
            <strong>Suggerimenti AI</strong>
            <p>Indica direttamente sul tabellone le carte che potrebbero essere collegate all’indizio.</p>
          </div>
          <button
            class="secondary ai-trigger"
            disabled={aiLoading || !connected}
            aria-pressed={aiOpen && aiCurrent}
            onclick={suggest}
            >{aiLoading
              ? 'Valutazione in corso…'
              : aiCurrent && aiOpen
                ? 'Nascondi suggerimenti'
                : aiCurrent
                  ? 'Mostra suggerimenti'
                  : 'Chiedi all’AI'}</button
          >
        </div>
        {#if aiError}<p class="ai-error" role="alert">{aiError}</p>{/if}
        {#if aiCurrent && aiOpen}
          <p class="ai-status" role="status"><span class="ai-status-mark" aria-hidden="true">AI</span>
            {aiRelated.length === 0
              ? 'Nessuna carta suggerita per questo indizio.'
              : aiRelated.length === 1
                ? 'Una carta evidenziata sul tabellone.'
                : `${aiRelated.length} carte evidenziate sul tabellone.`}
            <span class="ai-caution">Sono suggerimenti, non risposte certe. L’AI non conosce le identità.</span>
          </p>
        {/if}
      </section>
    {/if}
    <div class="table-controls">
      {#if canControl}{#if !game.clue}<form
            class="clue-form"
            onsubmit={(e) => {
              e.preventDefault();
              command({
                kind: 'clue',
                word: clueWord,
                number: Number(clueNumber)
              });
            }}
          >
            <label
              >Indizio<input
                bind:value={clueWord}
                maxlength="32"
                placeholder="Una sola parola"
                required
                disabled={busy || !connected}
              /></label
            ><label class="clue-count"
              >Numero<input
                type="number"
                bind:value={clueNumber}
                min="0"
                max={active.remaining}
                required
                disabled={busy || !connected}
              /></label
            ><button
              class="primary"
              disabled={busy || !connected || !clueWord.trim()}
              >Conferma indizio <Icon name="arrow" /></button
            >
          </form>{:else}<p class="play-hint">
            Scegli una parola, poi conferma la rivelazione.
          </p>{/if}<button
          class="secondary pass-button"
          disabled={busy || !connected}
          onclick={() => {
            passRevision = game.revision;
            passDialog.showModal();
          }}>Passa il turno <Icon name="arrow" /></button
        >{:else if spy}<p class="play-hint">
          Dai un indizio a voce: una parola e un numero. 0 significa tentativi
          illimitati.
        </p>{:else if game.status === 'playing'}<p class="play-hint">
          Tabellone pubblico · Le mosse si effettuano dal dispositivo
          dell’organizzatore.
        </p>{/if}
    </div>
    <div class="game-bottom">
      <div class="connection">
        <i class:offline={!connected}></i>{connected
          ? 'Tabellone sincronizzato'
          : 'Riconnessione…'}
      </div>
      <div class="bottom-actions">
        <button class="text-button" onclick={() => (showSharing = !showSharing)}
          >{showSharing ? 'Chiudi collegamenti' : 'Condividi partita'}</button
        >
        <details class="history">
          <summary>Registro mosse ({game.history.length})</summary>
          <ol>
            {#each [...game.history].reverse() as event}<li>
                <span>T{event.turn} · {game.teams[event.team].name}</span
                >{describe(event)}
              </li>{/each}{#if !game.history.length}<li>
                La missione deve ancora iniziare.
              </li>{/if}
          </ol>
        </details>
      </div>
    </div>
    {#if showSharing}<section class="share-panel">
        <h2>La stessa missione, due punti di vista.</h2>
        <label
          >Tabellone pubblico
          <div class="inline">
            <input
              readonly
              value={`${origin}/g/${id}`}
              onclick={(e) => e.currentTarget.select()}
            /><button
              class="secondary"
              onclick={() => copy(`${origin}/g/${id}`, 'Link pubblico')}
              aria-label="Copia link pubblico"><Icon name="copy" /></button
            >
          </div></label
        ><label
          >Mappa Spymaster
          <div class="inline">
            <input
              readonly
              value={`${origin}/g/${id}/spy`}
              onclick={(e) => e.currentTarget.select()}
            /><button
              class="secondary"
              onclick={() => copy(`${origin}/g/${id}/spy`, 'Link Spymaster')}
              aria-label="Copia link Spymaster"><Icon name="copy" /></button
            >
          </div></label
        >{#if hostKey}<details class="private-links">
            <summary
              ><Icon name="lock" /> Mostra accessi riservati all’organizzatore</summary
            >
            <p>
              Apri questa sezione fuori dalla proiezione. Il link di controllo
              permette di effettuare mosse.
            </p>
            {#if accessCode}<label
                >Codice Spymaster
                <div class="inline">
                  <input readonly value={accessCode} /><button
                    class="secondary"
                    aria-label="Copia codice Spymaster"
                    onclick={() => copy(accessCode, 'Codice Spymaster')}
                    ><Icon name="copy" /></button
                  >
                </div></label
              >{/if}<label
              >Link di controllo
              <div class="inline">
                <input
                  readonly
                  value={`${origin}/g/${id}#host=${hostKey}`}
                  onclick={(e) => e.currentTarget.select()}
                /><button
                  class="secondary"
                  aria-label="Copia link di controllo"
                  onclick={() =>
                    copy(
                      `${origin}/g/${id}#host=${hostKey}`,
                      'Link di controllo'
                    )}><Icon name="copy" /></button
                >
              </div></label
            >
          </details>{/if}
        <p role="status">{message}</p>
      </section>{/if}
  {/if}
</main>
<dialog bind:this={confirmDialog} onclose={() => (selected = null)}>
  <div class="dialog-top">
    <span>Conferma la scelta</span><button
      class="icon-button"
      aria-label="Annulla rivelazione"
      onclick={() => confirmDialog.close()}><Icon name="close" /></button
    >
  </div>
  <h2>{selected !== null && game ? game.cards[selected].word : ''}</h2>
  <p>
    Questa carta verrà rivelata a tutti.<br />La scelta non può essere
    annullata.
  </p>
  {#if error}<p class="error-message" role="alert">{error}</p>{/if}
  <div class="dialog-actions">
    <button
      class="secondary"
      onclick={() => confirmDialog.close()}
      disabled={busy}>Ripensaci</button
    ><button
      class="primary"
      disabled={busy || !connected}
      onclick={() =>
        command({ kind: 'reveal', card: selected, revision: selectedRevision })}
      >{busy ? 'Rivelazione…' : 'Rivela la carta'}<Icon name="eye" /></button
    >
  </div>
</dialog>
<dialog bind:this={passDialog}>
  <div class="dialog-top">
    <span>Fine del turno</span><button
      class="icon-button"
      aria-label="Annulla"
      onclick={() => passDialog.close()}><Icon name="close" /></button
    >
  </div>
  <h2>Passare la mano?</h2>
  <p>Il turno di {active?.name} termina e si passa alla prossima squadra.</p>
  <div class="dialog-actions">
    <button class="secondary" onclick={() => passDialog.close()}
      >Continua a giocare</button
    ><button
      class="primary"
      disabled={busy || !connected}
      onclick={() => command({ kind: 'pass', revision: passRevision })}
      >Passa il turno</button
    >
  </div>
</dialog>
<dialog bind:this={rulesDialog} class="rules-dialog">
  <div class="dialog-top">
    <span>Briefing della missione</span><button
      class="icon-button"
      aria-label="Chiudi regole"
      onclick={() => rulesDialog.close()}><Icon name="close" /></button
    >
  </div>
  <h2>Trova i tuoi agenti.</h2>
  <ol>
    <li>
      Lo Spymaster dà un indizio di <strong>una parola e un numero</strong>. Il
      numero indica quante carte sono collegate. Non sono ammessi nomi ancora
      coperti; accordatevi a voce su derivati e parole composte.
    </li>
    <li>
      L’organizzatore inserisce l’indizio. La squadra sceglie una carta e
      conferma: un agente proprio permette di continuare.
    </li>
    <li>
      Sono disponibili <strong>numero + 1 tentativi</strong>. Con 0 i tentativi
      sono illimitati. Potete sempre passare.
    </li>
    <li>
      Un civile o un agente avversario conclude il turno. L’agente avversario
      conta per la sua squadra.
    </li>
    <li>
      L’assassino <strong>elimina la squadra</strong>. Le altre continuano e le
      carte ancora coperte della squadra eliminata diventano civili.
    </li>
    <li>
      Vince chi trova tutti i propri agenti, oppure l’ultima squadra rimasta. La
      prima squadra è sorteggiata; il numero di agenti è quello configurato,
      senza bonus iniziale.
    </li>
  </ol>
  <p>
    Variante di gruppo ispirata a Nome in Codice. Gli Spymaster consultano la
    mappa dal proprio dispositivo e danno gli indizi a voce.
  </p>
</dialog>
