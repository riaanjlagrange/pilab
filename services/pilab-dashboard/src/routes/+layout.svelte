<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { fetchSystem } from '$lib/api';
  import { env } from '$env/dynamic/public';
  import './layout.css';
  import DiskPieChart      from '$lib/components/DiskPieChart.svelte';
  import DownloadIndicator from '$lib/components/DownloadIndicator.svelte';
  import NavMenu           from '$lib/components/NavMenu.svelte';
  import CommandPalette    from '$lib/components/CommandPalette.svelte';

  let paletteOpen = $state(false);
  let navOpen     = $state(false);
  let pilabName   = $state('');
  let { children } = $props();

  onMount(async () => {
    try {
      const system = await fetchSystem();
      pilabName = system.pilab_name || '';
    } catch (e) {
      console.error('Failed to load system name', e);
    }
  });

  // Close palette/nav on route change
  $effect(() => {
    $page.url.pathname;
    paletteOpen = false;
    navOpen     = false;
  });
</script>

<svelte:head>
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css"
  />
</svelte:head>

<!-- Global keyboard shortcut -->
<svelte:window
  onkeydown={(e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      paletteOpen = !paletteOpen;
    }
  }}
/>

<CommandPalette bind:open={paletteOpen} />
<NavMenu       bind:open={navOpen} />

<div class="min-h-screen bg-black text-gray-200">

  <!-- Nav bar -->
  <nav class="sticky top-0 z-50 border-b border-white/10 bg-black/95 backdrop-blur-md w-full">
    <div class="max-w-6xl mx-auto px-4 flex items-center h-12 gap-3">

      <!-- Hamburger -->
      <button
        onclick={() => (navOpen = !navOpen)}
        class="cursor-pointer text-gray-400 hover:text-gray-200 transition-colors p-1.5
               bg-black rounded-sm flex items-center justify-center
               border border-white/10 hover:border-white/20"
        aria-label="Open menu"
      >
        <i class="ti ti-menu-2 text-base"></i>
      </button>

      <!-- Logo -->
      <a href="/" class="font-mono text-sm font-bold text-gray-200 flex items-center gap-2 mr-2">
        <i class="ti ti-circuit-diode text-blue-400"></i>
        {pilabName || 'rpi'}
      </a>

      <!-- Search trigger -->
      <button
        onclick={() => (paletteOpen = !paletteOpen)}
        class="cursor-pointer flex-1 max-w-xs flex items-center gap-2 px-3 py-1.5
               rounded-md bg-white/5 border border-white/10 hover:border-white/20 transition-colors"
      >
        <i class="ti ti-search text-gray-600 text-sm"></i>
        <span class="hidden sm:block font-mono text-xs text-gray-600 flex-1 text-left">
          Search… <span class="text-gray-700">⌘K</span>
        </span>
      </button>

      <!-- Right side -->
      <div class="ml-auto flex items-center gap-3 font-mono text-xs text-gray-600">
        <DownloadIndicator />
        <DiskPieChart compact height={20} />
        <span class="hidden sm:flex items-center gap-1">
          <i class="ti ti-server text-xs"></i>
          {env.PUBLIC_HOST || '…'}
        </span>
      </div>

    </div>
  </nav>

  <!-- Page content -->
  <main class="max-w-6xl mx-auto px-4 py-6">
    {@render children()}
  </main>

</div>