<script>
  import { page } from '$app/state';
  import Game from '$lib/Game.svelte';
</script>

{#key page.params.id}<Game id={page.params.id.toUpperCase()} />{/key}
