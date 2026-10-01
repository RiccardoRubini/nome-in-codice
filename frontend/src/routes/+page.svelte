<script>
  import { goto } from '$app/navigation';
  import { api, colors, colorNames, names, storage } from '$lib/api';
  import Icon from '$lib/Icon.svelte';
  let teams = $state([
    { name: 'Volpe', color: colors[0], cards: 8 },
    { name: 'Falco', color: colors[1], cards: 8 }
  ]);
  let size = $state(25),
    civilians = $state(8),
    assassins = $state(1),
    spyCode = $state('');
  let busy = $state(false),
    error = $state(''),
    joinCode = $state('');
  let total = $derived(
    teams.reduce((n, t) => n + (Number(t.cards) || 0), 0) +
      Number(civilians) +
      Number(assassins)
  );
  let valid = $derived(
    total === size &&
      teams.every((t) => t.name.trim() && t.cards >= 1) &&
      civilians >= 0 &&
      assassins >= 0 &&
      (!spyCode || spyCode.trim().length >= 8)
  );
  let preview = $derived(
    [
      ...teams.flatMap((t, i) =>
        Array.from(
          { length: Math.min(30, Math.max(0, Number(t.cards) || 0)) },
          () => i
        )
      ),
      ...Array.from(
        { length: Math.min(30, Math.max(0, Number(civilians) || 0)) },
        () => -1
      ),
      ...Array.from(
        { length: Math.min(30, Math.max(0, Number(assassins) || 0)) },
        () => -2
      )
    ].slice(0, size)
  );
  function balance() {
    const available = size - Number(civilians) - Number(assassins);
    if (available < teams.length) return;
    teams = teams.map((t, i) => ({
      ...t,
      cards:
        Math.floor(available / teams.length) +
        (i < available % teams.length ? 1 : 0)
    }));
  }
  function count(n) {
    if (n < 2 || n > 5) return;
    if (n > teams.length) {
      const unused = colors.find((c) => !teams.some((t) => t.color === c));
      teams = [...teams, { name: names[n - 1], color: unused, cards: 1 }];
    } else teams = teams.slice(0, n);
    if (size - civilians - assassins < n)
      civilians = Math.max(0, size - assassins - n);
    balance();
  }
  function changeColor(i, value) {
    const other = teams.findIndex((t) => t.color === value);
    if (other !== -1 && other !== i) teams[other].color = teams[i].color;
    teams[i].color = value;
  }
  async function start() {
    if (!valid || busy) return;
    busy = true;
    error = '';
    try {
      const result = await api('/games', {
        method: 'POST',
        body: JSON.stringify({
          teams,
          size,
          civilians: Number(civilians),
          assassins: Number(assassins),
          spy_code: spyCode.trim()
        })
      });
      storage.set(`host:${result.game.id}`, result.host_key);
      if (result.spy_code)
        storage.set(`spy:${result.game.id}`, result.spy_code);
      await goto(
        `/g/${result.game.id}#host=${encodeURIComponent(result.host_key)}`
      );
    } catch (e) {
      error = e.message;
    } finally {
      busy = false;
    }
  }
  function join() {
    if (/^[a-zA-Z0-9]{6}$/.test(joinCode.trim()))
      goto(`/g/${joinCode.trim().toUpperCase()}`);
  }
  const examples = [
    'LUNA',
    'PONTE',
    'AQUILA',
    'CHIAVE',
    'BOSCO',
    'RADIO',
    'CORONA',
    'MARE',
    'TORRE',
    'OMBRA',
    'PIANO',
    'FUOCO',
    'VETRO',
    'NAVE',
    'ROSA',
    'GHIACCIO',
    'TEMPIO',
    'VOLPE',
    'STELLA',
    'ORO',
    'CAMPO',
    'MASCHERA',
    'ANELLO',
    'VENTO',
    'DRAGO',
    'PERLA',
    'TRENO',
    'CARTA',
    'ISOLA',
    'FARO'
  ];
</script>

<header class="masthead">
  <a class="brand" href="/"
    ><Icon name="shield" size={27} /><span>NOME IN CODICE</span></a
  >
  <span class="masthead-note">Parole in chiaro. Identità segrete.</span>
  <details class="join">
    <summary>Hai un codice partita?</summary>
    <form
      onsubmit={(e) => {
        e.preventDefault();
        join();
      }}
    >
      <label for="join">Codice partita</label>
      <div class="inline">
        <input
          id="join"
          bind:value={joinCode}
          maxlength="6"
          placeholder="ABC123"
          autocomplete="off"
          pattern="[A-Za-z0-9]{6}"
          required
        /><button class="primary" type="submit"
          >Entra <Icon name="arrow" /></button
        >
      </div>
    </form>
  </details>
</header>
<main class="setup-shell">
  <div class="page-heading">
    <div>
      <h1>Prepara la partita.</h1>
      <p>Configura squadre e carte, poi condividi il tabellone.</p>
    </div>
  </div>
  <div class="setup-columns">
    <form
      class="configuration"
      onsubmit={(e) => {
        e.preventDefault();
        start();
      }}
    >
      <section class="form-section">
        <div class="section-title">
          <h2>Le squadre</h2>
          <div class="stepper">
            <button
              type="button"
              aria-label="Rimuovi una squadra"
              disabled={teams.length <= 2}
              onclick={() => count(teams.length - 1)}>−</button
            ><span>{teams.length}</span><button
              type="button"
              aria-label="Aggiungi una squadra"
              disabled={teams.length >= 5}
              onclick={() => count(teams.length + 1)}>+</button
            >
          </div>
        </div>
        <p class="muted">Nomi in codice, colori e agenti da trovare.</p>
        <div class="team-table">
          <div class="team-table-head">
            <span>Identità</span><span>Squadra</span><span>Agenti</span>
          </div>
          {#each teams as team, i}<div class="team-row">
              <label class="color-select" style:--team={team.color}
                ><span aria-hidden="true">{String.fromCharCode(65 + i)}</span
                ><select
                  aria-label={`Colore squadra ${i + 1}`}
                  value={team.color}
                  onchange={(e) => changeColor(i, e.currentTarget.value)}
                  >{#each colors as color, j}<option value={color}
                      >{colorNames[j]}</option
                    >{/each}</select
                ></label
              ><input
                aria-label={`Nome squadra ${i + 1}`}
                bind:value={team.name}
                maxlength="24"
                required
              /><input
                class="number"
                aria-label={`Agenti squadra ${i + 1}`}
                type="number"
                min="1"
                max={Math.max(1, size - total + Number(team.cards))}
                bind:value={team.cards}
                required
              />
            </div>{/each}
        </div>
      </section>
      <section class="form-section">
        <h2>Il campo di gioco</h2>
        <div class="field-grid">
          <fieldset class="board-choice">
            <legend>Dimensione tabellone</legend>
            <div class="segmented">
              {#each [25, 30] as option}<button
                  type="button"
                  class:chosen={size === option}
                  aria-pressed={size === option}
                  onclick={() => {
                    size = option;
                    balance();
                  }}>5 × {option / 5}<span>{option} carte</span></button
                >{/each}
            </div>
          </fieldset>
          <label
            >Civili<input
              type="number"
              min="0"
              max={size - teams.length - assassins}
              bind:value={civilians}
              onchange={balance}
            /></label
          ><label
            >Assassini<input
              type="number"
              min="0"
              max={size - teams.length - civilians}
              bind:value={assassins}
              onchange={balance}
            /></label
          >
        </div>
        <div class="allocation-note">
          <span class:error-text={total !== size}
            >{total} di {size} carte assegnate{total === size
              ? ' · Campo completo'
              : ''}</span
          ><button type="button" class="text-button" onclick={balance}
            >Distribuisci agenti</button
          >
        </div>
      </section>
      <section class="form-section access-section">
        <div>
          <h2><Icon name="lock" /> Accesso Spymaster</h2>
          <p class="muted">
            La mappa delle identità si apre su un secondo dispositivo.
          </p>
        </div>
        <label class="sr-only" for="spy-code"
          >Codice Spymaster facoltativo, almeno 8 caratteri</label
        ><input
          id="spy-code"
          type="password"
          bind:value={spyCode}
          minlength="8"
          maxlength="80"
          placeholder="Codice segreto (facoltativo)"
          autocomplete="new-password"
        />
        <p class="field-help">
          Lascia vuoto per accesso libero. Inserisci un codice per proteggerla.
        </p>
      </section>
      {#if error}<p class="error-message" role="alert">{error}</p>{/if}
      <button
        class="primary start-button"
        disabled={!valid || busy}
        type="submit"
        ><span>{busy ? 'Preparazione in corso…' : 'Avvia la missione'}</span
        ><Icon name="arrow" size={24} /></button
      >
      <p class="start-note">
        Prima squadra sorteggiata. Nessuna registrazione.
      </p>
    </form>
    <aside class="preview-panel">
      <div class="preview-top">
        <h2>Il vostro tavolo</h2>
        <span class="small-label">ANTEPRIMA · {size} CARTE</span>
      </div>
      <div
        class="mini-board"
        aria-label="Anteprima illustrativa della distribuzione, non il tabellone della partita"
      >
        {#each Array.from({ length: size }) as _, i}{@const owner = preview[i]}
          <div
            class="mini-card"
            class:mini-assassin={owner === -2}
            class:mini-civilian={owner === -1 || owner === undefined}
            style:--team={owner >= 0 ? teams[owner].color : '#e4e3d8'}
          >
            <span class="mini-index">{String(i + 1).padStart(2, '0')}</span
            ><strong style:--word-length={examples[i].length}>{examples[i]}</strong><span class="mini-owner"
              >{owner >= 0
                ? teams[owner].name
                : owner === -2
                  ? 'ASSASSINO'
                  : 'CIVILE'}</span
            >
          </div>{/each}
      </div>
      <p class="preview-caption">
        Solo un’anteprima. Parole e identità vengono mescolate all’avvio.
      </p>
      <div class="legend">
        {#each teams as team}<span
            ><i style:background={team.color}></i>{team.name}
            <b>{team.cards}</b></span
          >{/each}<span
          ><i class="civilian-dot"></i>Civili <b>{civilians}</b></span
        ><span><i class="assassin-dot"></i>Assassini <b>{assassins}</b></span>
      </div>
      <div class="briefing">
        <h3>Un indizio. Molte possibilità.</h3>
        <p>
          Lo Spymaster conosce le identità. Una parola e un numero guidano la
          squadra verso i propri agenti. Un errore passa il turno; un assassino
          elimina la squadra.
        </p>
        <div class="briefing-bottom">
          <Icon name="eye" /><span
            >Proietta il tabellone.<br />Tieni la mappa segreta sul telefono.</span
          >
        </div>
      </div>
    </aside>
  </div>
  <footer class="site-footer">
    <span>Un gioco di intuizione, parole e complicità.</span><span
      >Da 2 a 5 squadre · Tutti nella stessa stanza</span
    >
  </footer>
</main>
