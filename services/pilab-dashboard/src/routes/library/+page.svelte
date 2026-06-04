<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchRadarrMedia, fetchSonarrMedia } from '$lib/api';
  import type { RadarrMedia, SonarrMedia, SearchResult, DownloadedMovie, DownloadedSeries } from '$lib/types.d.ts';
  import { fromDownloadedMovie, fromDownloadedSeries } from '$lib/adapters';
  import MediaScrollCard  from '$lib/components/MediaScrollCard.svelte';
  import MediaDetailModal from '$lib/components/MediaDetailModal.svelte';

  // ─── State ──────────────────────────────────────────────────────────────
  let radarr   = $state<RadarrMedia | null>(null);
  let sonarr   = $state<SonarrMedia | null>(null);
  let loading  = $state(true);
  let error    = $state('');
  let filter   = $state<'all' | 'movies' | 'series'>('all');
  let search   = $state('');
  let selected = $state<SearchResult | null>(null);

  // ─── Derived ────────────────────────────────────────────────────────────
  let movies = $derived<DownloadedMovie[]>(radarr?.downloaded ?? []);
  let series = $derived<DownloadedSeries[]>(sonarr?.downloaded ?? []);

  let filteredMovies = $derived(
    (filter === 'series' ? [] : movies).filter(m =>
      !search || m.title.toLowerCase().includes(search.toLowerCase())
    )
  );

  let filteredSeries = $derived(
    (filter === 'movies' ? [] : series).filter(s =>
      !search || s.title.toLowerCase().includes(search.toLowerCase())
    )
  );

  let totalSize = $derived(
    [...movies, ...series].reduce((sum, item) => sum + item.size_gb, 0)
  );

  function openModal(meta: SearchResult) { selected = meta; }
  function closeModal()                  { selected = null; }

  function handleDeleted(id: number, type: 'movie' | 'series') {
    if (type === 'movie' && radarr) {
      radarr = { ...radarr, downloaded: radarr.downloaded.filter(m => m.id !== id) };
    } else if (type === 'series' && sonarr) {
      sonarr = { ...sonarr, downloaded: sonarr.downloaded.filter(s => s.id !== id) };
    }
    selected = null;
  }

  // ─── Load ────────────────────────────────────────────────────────────────
  async function loadData() {
    loading = true;
    error   = '';
    try {
      const [rRes, sRes] = await Promise.allSettled([fetchRadarrMedia(), fetchSonarrMedia()]);
      if (rRes.status === 'fulfilled') radarr = rRes.value;
      if (sRes.status === 'fulfilled') sonarr = sRes.value;
    } catch (e) {
      error = 'Failed to load library.';
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(loadData);
</script>

<!-- Header -->
<div class="flex items-start justify-between mb-6 gap-4 flex-wrap">
  <div>
    <h1 class="font-mono text-sm font-bold text-gray-200 flex items-center gap-2">
      <i class="ti ti-database text-[#e5a00d]"></i>
      Library
    </h1>
    {#if !loading}
      <p class="font-mono text-xs text-gray-600 mt-0.5">
        {movies.length} movie{movies.length !== 1 ? 's' : ''}
        · {series.length} series
        · {totalSize.toFixed(1)} GB
      </p>
    {/if}
  </div>

  <!-- Filters -->
  <div class="flex items-center gap-2 flex-wrap">
    <!-- search -->
    <div class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-white/5
                border border-white/10 focus-within:border-white/25 transition-colors">
      <i class="ti ti-search text-gray-600 text-xs"></i>
      <input
        type="text"
        placeholder="Filter…"
        bind:value={search}
        class="bg-transparent font-mono text-xs text-gray-300 placeholder-gray-700
               outline-none w-32 focus:w-44 transition-all duration-200"
      />
    </div>

    <!-- type toggle -->
    {#each [['all', 'All'], ['movies', 'Movies'], ['series', 'Series']] as [val, label]}
      <button
        onclick={() => (filter = val as typeof filter)}
        class="font-mono text-xs px-3 py-1.5 rounded-md border transition-colors
               {filter === val
                 ? 'bg-[#e5a00d]/10 border-[#e5a00d]/40 text-[#e5a00d]'
                 : 'bg-white/5 border-white/10 text-gray-500 hover:text-gray-300 hover:border-white/20'}"
      >
        {label}
      </button>
    {/each}
  </div>
</div>

{#if error}
  <div class="mb-4 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-3">
    <i class="ti ti-alert-circle text-sm text-red-400"></i>
    <span class="font-mono text-xs text-red-400">{error}</span>
  </div>
{/if}

<!-- ── Movies ─────────────────────────────────────────────────────────────── -->
{#if filter !== 'series'}
  <section class="mb-8">
    {#if filter === 'all'}
      <p class="font-mono text-xs text-gray-500 uppercase tracking-widest mb-3
                flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10">
        Movies
        <span class="text-gray-700 normal-case tracking-normal">{filteredMovies.length}</span>
      </p>
    {/if}

    {#if loading}
      <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
        {#each Array(14) as _, i (i)}
          <div class="aspect-[2/3] rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
        {/each}
      </div>
    {:else if filteredMovies.length === 0}
      <div class="flex flex-col items-center justify-center py-12 text-center">
        <i class="ti ti-movie-off text-3xl text-gray-700 mb-2"></i>
        <p class="font-mono text-xs text-gray-600">
          {search ? 'No movies match your filter.' : 'No movies downloaded yet.'}
        </p>
      </div>
    {:else}
      <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
        {#each filteredMovies as item (item.id)}
          <MediaScrollCard item={fromDownloadedMovie(item)} onselect={openModal} />
        {/each}
      </div>
    {/if}
  </section>
{/if}

<!-- ── Series ─────────────────────────────────────────────────────────────── -->
{#if filter !== 'movies'}
  <section>
    {#if filter === 'all'}
      <p class="font-mono text-xs text-gray-500 uppercase tracking-widest mb-3
                flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10">
        Series
        <span class="text-gray-700 normal-case tracking-normal">{filteredSeries.length}</span>
      </p>
    {/if}

    {#if loading}
      <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
        {#each Array(14) as _, i (i)}
          <div class="aspect-[2/3] rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
        {/each}
      </div>
    {:else if filteredSeries.length === 0}
      <div class="flex flex-col items-center justify-center py-12 text-center">
        <i class="ti ti-device-tv-off text-3xl text-gray-700 mb-2"></i>
        <p class="font-mono text-xs text-gray-600">
          {search ? 'No series match your filter.' : 'No series downloaded yet.'}
        </p>
      </div>
    {:else}
      <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
        {#each filteredSeries as item (item.id)}
          <MediaScrollCard item={fromDownloadedSeries(item)} onselect={openModal} />
        {/each}
      </div>
    {/if}
  </section>
{/if}

<!-- ── Modal ──────────────────────────────────────────────────────────────── -->
{#if selected}
  <MediaDetailModal
    result={selected}
    onclose={closeModal}
    ondeleted={handleDeleted}
  />
{/if}