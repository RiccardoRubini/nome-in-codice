<script>
  let { name, size = 20 } = $props();
  const paths = {
    arrow: 'M4 12h16m-6-6 6 6-6 6',
    lock: 'M6 10h12v11H6zM8 10V6a4 4 0 0 1 8 0v4',
    eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
    copy: 'M8 8h12v13H8zM16 8V3H3v13h5',
    check: 'm5 12 4 4L19 6',
    close: 'm6 6 12 12M18 6 6 18',
    expand: 'M8 3H3v5M16 3h5v5M3 16v5h5M21 16v5h-5',
    shield: 'M12 2 3 6v6c0 5 9 10 9 10s9-5 9-10V6zM8 12l3 3 5-6',
    plus: 'M12 5v14M5 12h14'
  };
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.7"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"><path d={paths[name] || paths.arrow} /></svg
>
