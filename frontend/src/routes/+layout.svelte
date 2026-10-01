<script>
  import '@fontsource/barlow-condensed/latin-600.css';
  import '@fontsource/barlow-condensed/latin-700.css';
  import '@fontsource/dm-sans/latin-400.css';
  import '@fontsource/dm-sans/latin-500.css';
  import '@fontsource/dm-sans/latin-600.css';
  import '@fontsource/dm-sans/latin-700.css';
  import '$lib/app.css';
  let { children } = $props();
</script>

<svelte:head
  ><title>Nome in codice</title><meta
    name="description"
    content="Il gioco di parole e agenti segreti per la tua squadra. Da 2 a 5 squadre, un tabellone condiviso."
  /></svelte:head
>
{@render children()}
