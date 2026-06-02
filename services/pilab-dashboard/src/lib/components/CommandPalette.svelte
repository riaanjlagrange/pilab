<script lang="ts">
  import type { SearchResult } from '$lib/types.d.ts';
  import { searchPlex, searchRadarr, searchSonarr } from '$lib/api';
  import { page } from '$app/stores';
  import SearchResultComponent from './SearchResult.svelte';
  import MediaDetailModal from './MediaDetailModal.svelte';

  let { open = $bindable(false) }: { open: boolean } = $props();

  let query        = $state('');
  let results      = $state<SearchResult[]>([]);
  let loading      = $state(false);
  let selected     = $state<SearchResult | null>(null);
  let inputEl      = $state<HTMLInputElement | null>(null);
  let debounceTimer: ReturnType<typeof setTimeout>;

  type Prefix = 'plex' | 'radarr' | 'sonarr' | null;

  let prefix = $derived<Prefix>(
    query.startsWith('/radarr ') ? 'radarr' :
    query.startsWith('/sonarr ') ? 'sonarr' :
    query.startsWith('/plex ')   ? 'plex'   : null
  );

  let displayQuery = $derived(
    prefix ? query.slice(prefix.length + 2) : query
  );

  let prefixHint = $derived(
    prefix === 'radarr' ? { label: 'radarr', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' }   :
    prefix === 'sonarr' ? { label: 'sonarr', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' } :
    prefix === 'plex'   ? { label: 'plex',   color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' } :
    null
  );

  let inputValue = $derived.by(() => {
    if (prefix) return displayQuery;
    return query;
  });

  function handleInputChange(e: Event) {
    const input = e.target as HTMLInputElement;
    if (prefix) {
      query = `/${prefix} ${input.value}`;
    } else {
      query = input.value;
    }
  }

  $effect(() => {
    if (open) {
      setTimeout(() => inputEl?.focus(), 50);
    } else {
      query    = '';
      results  = [];
      selected = null;
    }
  });

  $effect(() => {
    $page.url.pathname;
    open = false;
  });

  $effect(() => {
    const q = displayQuery.trim();
    clearTimeout(debounceTimer);
    if (!q) { results = []; return; }

    debounceTimer = setTimeout(async () => {
      loading = true;
      try {
        if (prefix === 'radarr')      results = await searchRadarr(q);
        else if (prefix === 'sonarr') results = await searchSonarr(q);
        else                          results = await searchPlex(q);
      } finally {
        loading = false;
      }
    }, 300);
  });

  function handleKeydown(e: KeyboardEvent) {
    if (!open) return;
    if (e.key === 'Escape') {
      if (selected) selected = null;
      else open = false;
    }
  }

  function handleGlobalKeydown(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      open = !open;
    }
  }
</script>

<svelte:window onkeydown={(e) => { handleGlobalKeydown(e); handleKeydown(e); }} />

{#if open}
  <!-- Backdrop -->
  <div
    class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex flex-col items-center pt-24 px-4"
    role="button"
    tabindex="0"
    aria-label="Close command palette"
    onclick={() => (open = false)}
    onkeydown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        open = false;
      }
    }}
  >
    <!-- Palette panel -->
    <div
      class="w-full max-w-2xl bg-[#0d0d0d] border border-white/10 rounded-sm shadow-2xl overflow-hidden"
      role="dialog"
      aria-modal="true"
      tabindex="-1"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => {
        if (e.key !== 'Escape') e.stopPropagation();
      }}
    >
      <!-- Input row -->
      <div class="flex items-center gap-2 px-4 py-3 border-b border-white/10">
        {#if prefixHint}
          <span class="font-mono text-xs px-2 py-0.5 rounded border shrink-0 {prefixHint.color}">
            /{prefixHint.label}
          </span>
        {:else}
          <i class="ti ti-search text-gray-500 text-base shrink-0"></i>
        {/if}

        <input
          bind:this={inputEl}
          value={inputValue}
          oninput={handleInputChange}
          onkeydown={(e) => {
            if (e.key === 'Backspace' && inputValue === '' && prefix) {
              query = '';
            }
          }}
          placeholder={prefix ? `Search ${prefix}…` : 'Search library… or /radarr /sonarr'}
          class="cursor-pointer flex-1 bg-transparent font-mono text-sm text-gray-200 placeholder-gray-600 focus:outline-none"
        />
        {#if loading}
          <i class="ti ti-loader-2 animate-spin text-gray-500 text-sm shrink-0"></i>
        {/if}

        <kbd class="font-mono text-[10px] text-gray-600 border border-white/10 rounded px-1.5 py-0.5 shrink-0">
          esc
        </kbd>
      </div>

      <!-- Hints (when empty) -->
      {#if !displayQuery.trim()}
        <div class="px-4 py-5 space-y-1.5">
          <p class="font-mono text-[11px] text-gray-600 mb-3">Prefixes</p>
          {#each [
            { prefix: '/radarr', desc: 'Search for movies to download', color: 'text-blue-400' },
            { prefix: '/sonarr', desc: 'Search for shows to download',  color: 'text-purple-400' },
            { prefix: '/plex',   desc: 'Search your local library',     color: 'text-yellow-400' },
          ] as hint}
            <div class="flex items-center gap-3">
              <span class="font-mono text-xs {hint.color} w-20 shrink-0">{hint.prefix}</span>
              <span class="font-mono text-xs text-gray-600">{hint.desc}</span>
            </div>
          {/each}
        </div>

      <!-- Results -->
      {:else if results.length > 0}
        <div class="max-h-[420px] overflow-y-auto p-2 space-y-0.5">
          {#each results as result (result.tmdb_id ?? result.tvdb_id ?? result.title)}
            <SearchResultComponent
              {result}
              onclick={(r) => (selected = r)}
            />
          {/each}
        </div>

      <!-- No results -->
      {:else if !loading}
        <div class="px-4 py-8 text-center">
          <p class="font-mono text-sm text-gray-600">No results for "{displayQuery}"</p>
        </div>
      {/if}
    </div>
  </div>

  <!-- Detail modal layered on top -->
  {#if selected}
    <MediaDetailModal
      result={selected}
      onclose={() => (selected = null)}
    />
  {/if}
{/if}