<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchPlexMedia, fetchPlexActive, fetchRadarrMedia, fetchSonarrMedia } from '$lib/api';
  import type { PlexMedia, RadarrMedia, SonarrMedia, PlexSession, SearchResult } from '$lib/types.d.ts';
  import {
    fromPlexItem,
    fromTrendingMovie,
    fromTrendingSeries,
    fromDownloadedMovie,
    fromDownloadedSeries,
  } from '$lib/adapters';
  import MediaScrollCard  from '$lib/components/MediaScrollCard.svelte';
  import NowPlaying       from '$lib/components/NowPlaying.svelte';
  import MediaDetailModal from '$lib/components/MediaDetailModal.svelte';

  // ─── State ────────────────────────────────────────────────────────────────
  let plexMedia  = $state<PlexMedia | null>(null);
  let active     = $state<PlexSession[]>([]);
  let radarr     = $state<RadarrMedia | null>(null);
  let sonarr     = $state<SonarrMedia | null>(null);
  let loading    = $state(true);

  // modal
  let selected   = $state<SearchResult | null>(null);

  function openModal(meta: SearchResult) { selected = meta; }
  function closeModal()                  { selected = null; }

  // ─── Load ─────────────────────────────────────────────────────────────────
  async function loadAll(isBackground = false) {
    if (!isBackground) loading = true;
    const [plexRes, activeRes, radarrRes, sonarrRes] = await Promise.allSettled([
      fetchPlexMedia(),
      fetchPlexActive(),
      fetchRadarrMedia(),
      fetchSonarrMedia(),
    ]);
    if (plexRes.status   === 'fulfilled') plexMedia = plexRes.value;
    if (activeRes.status === 'fulfilled') active    = activeRes.value;
    if (radarrRes.status === 'fulfilled') radarr    = radarrRes.value;
    if (sonarrRes.status === 'fulfilled') sonarr    = sonarrRes.value;
    if (!isBackground) loading = false;
  }

  onMount(() => {
    loadAll();
    const interval = setInterval(() => loadAll(true), 30_000);
    return () => clearInterval(interval);
  });

  // ─── Section label helper ─────────────────────────────────────────────────
  const sectionLabel = 'font-mono text-xs text-gray-500 uppercase tracking-widest mb-3';
  const sectionClass = 'mb-8';
</script>

<!-- ── Now playing ─────────────────────────────────────────────────────────── -->
{#if active.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Now Playing</p>
    <div class="space-y-3">
      {#each active as session (session.rating_key)}
        <NowPlaying item={session} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Continue watching ───────────────────────────────────────────────────── -->
{#if loading}
  <section class={sectionClass}>
    <p class={sectionLabel}>Continue Watching</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each Array(7) as _, i (i)}
        <div class="aspect-[2/3] rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
      {/each}
    </div>
  </section>
{:else if plexMedia && plexMedia.continueWatching.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Continue Watching</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each plexMedia.continueWatching as item (item.rating_key)}
        <MediaScrollCard item={fromPlexItem(item)} onselect={openModal} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Trending movies ─────────────────────────────────────────────────────── -->
{#if loading}
  <section class={sectionClass}>
    <p class={sectionLabel}>Trending Movies</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each Array(7) as _, i (i)}
        <div class="aspect-[2/3] rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
      {/each}
    </div>
  </section>
{:else if radarr && radarr.trending.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Trending Movies</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each radarr.trending as item (item.tmdb_id ?? item.title)}
        <MediaScrollCard item={fromTrendingMovie(item)} onselect={openModal} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Trending series ─────────────────────────────────────────────────────── -->
{#if loading}
  <section class={sectionClass}>
    <p class={sectionLabel}>Trending Series</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each Array(7) as _, i (i)}
        <div class="aspect-[2/3] rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
      {/each}
    </div>
  </section>
{:else if sonarr && sonarr.trending.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Trending Series</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each sonarr.trending as item (item.id)}
        <MediaScrollCard item={fromTrendingSeries(item)} onselect={openModal} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Plex library — movies ───────────────────────────────────────────────── -->
{#if !loading && plexMedia && plexMedia.movies.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Movies in Library</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each plexMedia.movies as item (item.rating_key)}
        <MediaScrollCard item={fromPlexItem(item)} onselect={openModal} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Plex library — series ───────────────────────────────────────────────── -->
{#if !loading && plexMedia && plexMedia.series.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Series in Library</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each plexMedia.series as item (item.rating_key)}
        <MediaScrollCard item={fromPlexItem(item)} onselect={openModal} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Downloaded movies (Radarr) ─────────────────────────────────────────── -->
{#if !loading && radarr && radarr.downloaded.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Downloaded Movies</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each radarr.downloaded as item (item.id)}
        <MediaScrollCard item={fromDownloadedMovie(item)} onselect={openModal} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Downloaded series (Sonarr) ─────────────────────────────────────────── -->
{#if !loading && sonarr && sonarr.downloaded.length > 0}
  <section class={sectionClass}>
    <p class={sectionLabel}>Downloaded Series</p>
    <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
      {#each sonarr.downloaded as item (item.id)}
        <MediaScrollCard item={fromDownloadedSeries(item)} onselect={openModal} />
      {/each}
    </div>
  </section>
{/if}

<!-- ── Modal ──────────────────────────────────────────────────────────────── -->
{#if selected}
  <MediaDetailModal result={selected} onclose={closeModal} />
{/if}