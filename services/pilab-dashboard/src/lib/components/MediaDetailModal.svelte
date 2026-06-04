<script lang="ts">
  import type { SearchResult, ServiceProfiles, RequestPayload } from '$lib/types.d.ts';
  import { getRadarrProfiles, getSonarrProfiles, requestMovie, requestShow, deleteMovie, deleteSeries } from '$lib/api';
  import { env } from '$env/dynamic/public';
  import Button from './Button.svelte';

  let { result, onclose, ondeleted }: {
    result:     SearchResult;
    onclose:    () => void;
    ondeleted?: (id: number, type: 'movie' | 'series') => void;
  } = $props();

  type RequestState = 'idle' | 'selecting' | 'loading' | 'done' | 'exists' | 'error';
  type DeleteState  = 'idle' | 'confirm' | 'deleting' | 'error';

  let requestState = $state<RequestState>('idle');
  let deleteState  = $state<DeleteState>('idle');
  let profiles     = $state<ServiceProfiles | null>(null);
  let selectedQP   = $state<number | null>(null);
  let selectedRoot = $state<string | null>(null);
  let errorMsg     = $state('');
  let deleteError  = $state('');

  // ── Presence logic ────────────────────────────────────────────────────────
  // "In library" means: Plex has it, OR Radarr/Sonarr has a file for it
  let inLibrary = $derived(
    (result.in_plex ?? result.source === 'plex') ||
    (result.in_radarr ?? false) ||
    (result.in_sonarr ?? false)
  );

  // Already queued = in Radarr/Sonarr but NOT yet in Plex
  let inQueue = $derived(
    !(result.in_plex ?? result.source === 'plex') &&
    ((result.in_radarr ?? false) || (result.in_sonarr ?? false))
  );

  // Deletable if we have a Radarr or Sonarr ID
  let deletableId   = $derived(result.radarr_id ?? result.sonarr_id ?? null);
  let deletableType = $derived<'movie' | 'series'>(result.type === 'movie' ? 'movie' : 'series');

  // Service URLs — always available
  let isMovie      = $derived(result.type === 'movie');
  let serviceLabel = $derived(isMovie ? 'Radarr' : 'Sonarr');
  let serviceUrl   = $derived(
    `http://${env.PUBLIC_HOST}:${isMovie ? '7878' : '8989'}`
  );

  // Plex search link — best we can do without a direct key
  let plexSearchUrl = $derived(
    result.plex_link ||
    `http://${env.PUBLIC_HOST}:32400/web/index.html#!/search?query=${encodeURIComponent(result.title)}`
  );

  async function openRequestPanel() {
    requestState = 'selecting';
    profiles     = isMovie ? await getRadarrProfiles() : await getSonarrProfiles();
    selectedQP   = profiles.quality_profiles[0]?.id  ?? null;
    selectedRoot = profiles.root_folders[0]?.path     ?? null;
  }

  async function confirmRequest() {
    if (!selectedQP || !selectedRoot) return;
    requestState = 'loading';
    const payload: RequestPayload = { quality_profile_id: selectedQP, root_folder: selectedRoot };
    if (isMovie) payload.tmdb_id = result.tmdb_id;
    else         payload.tvdb_id = result.tvdb_id;
    const res = isMovie ? await requestMovie(payload) : await requestShow(payload);
    if (res.ok)                              requestState = 'done';
    else if (res.error === 'already_exists') requestState = 'exists';
    else { requestState = 'error'; errorMsg = res.error ?? 'Unknown error'; }
  }

  async function confirmDelete() {
    if (!deletableId) return;
    deleteState = 'deleting';
    deleteError = '';
    try {
      if (deletableType === 'movie') await deleteMovie(deletableId);
      else                           await deleteSeries(deletableId);
      ondeleted?.(deletableId, deletableType);
      onclose();
    } catch {
      deleteError = 'Delete failed. Check the API.';
      deleteState = 'error';
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      if (deleteState === 'confirm') { deleteState = 'idle'; return; }
      onclose();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- Backdrop -->
<div
  class="fixed inset-0 z-60 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
  role="button"
  tabindex="0"
  onclick={onclose}
  onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') onclose(); }}
  aria-label="Close modal"
>
  <!-- Modal -->
  <div
    class="relative w-full max-w-xl bg-[#111] border border-white/10 rounded-xl
           overflow-hidden shadow-2xl flex flex-col max-h-[85vh]"
    role="button"
    tabindex="0"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => { if (e.key !== 'Escape') e.stopPropagation(); }}
    aria-label="Media details"
  >
    <!-- Fanart banner -->
    {#if result.fanart_url}
      <div class="h-48 w-full overflow-hidden relative shrink-0">
        <img src={result.fanart_url} alt="" class="w-full h-full object-cover opacity-40" />
        <div class="absolute inset-0 bg-gradient-to-b from-transparent to-[#111]"></div>
      </div>
    {:else}
      <div class="h-6 shrink-0"></div>
    {/if}

    <!-- Close -->
    <button
      onclick={onclose}
      class="cursor-pointer absolute top-3 right-3 z-10 w-7 h-7 flex items-center justify-center
             rounded-md bg-black/50 border border-white/10 text-gray-400 hover:text-white
             hover:border-white/30 transition-all"
      aria-label="Close"
    >
      <i class="ti ti-x text-sm"></i>
    </button>

    <!-- Scrollable body -->
    <div class="overflow-y-auto flex-1">
      <div class="flex gap-5 px-6 pb-6 {result.fanart_url ? '-mt-10' : 'pt-2'}">

        <!-- Poster -->
        <div class="shrink-0 w-28 h-40 rounded-lg overflow-hidden border border-white/10
                    shadow-xl bg-white/5 flex items-center justify-center">
          {#if result.poster_url}
            <img src={result.poster_url} alt={result.title} class="w-full h-full object-cover" />
          {:else}
            <i class="ti ti-{result.type === 'show' || result.type === 'series' ? 'device-tv' : 'movie'} text-gray-600 text-3xl"></i>
          {/if}
        </div>

        <!-- Details -->
        <div class="flex-1 min-w-0 pt-2">

          <!-- Title + year -->
          <div class="flex items-start gap-2 flex-wrap">
            <h2 class="font-mono font-bold text-gray-100 text-base leading-tight">{result.title}</h2>
            {#if result.year}
              <span class="font-mono text-xs text-gray-500 mt-0.5">{result.year}</span>
            {/if}
          </div>

          <!-- Meta row -->
          <div class="flex items-center gap-3 mt-1.5 flex-wrap">
            {#if result.rating}
              <span class="flex items-center gap-1 font-mono text-xs text-yellow-400">
                <i class="ti ti-star-filled text-xs"></i>
                {result.rating.toFixed(1)}
              </span>
            {/if}
            {#if result.network}
              <span class="font-mono text-xs text-gray-500">{result.network}</span>
            {/if}
            {#if result.status}
              <span class="font-mono text-xs text-gray-500 capitalize">{result.status}</span>
            {/if}
            <span class="font-mono text-[10px] px-1.5 py-0.5 rounded border
                         {result.type === 'show' || result.type === 'series'
                           ? 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                           : 'bg-blue-500/20 text-blue-400 border-blue-500/30'}">
              {result.type === 'series' ? 'show' : result.type}
            </span>
          </div>

          <!-- Overview -->
          {#if result.overview}
            <p class="font-mono text-xs text-gray-400 leading-relaxed mt-3 line-clamp-4">
              {result.overview}
            </p>
          {/if}

          <!-- ── Actions ───────────────────────────────────────────────── -->
          <div class="mt-4 space-y-3">

            <!-- Library status badge -->
            {#if inLibrary}
              <span class="inline-flex items-center gap-1.5 font-mono text-xs text-green-400
                           bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-md">
                <i class="ti ti-check text-xs"></i>
                In library
              </span>
            {:else if inQueue}
              <span class="inline-flex items-center gap-1.5 font-mono text-xs text-yellow-400
                           bg-yellow-500/10 border border-yellow-500/20 px-3 py-1.5 rounded-md">
                <i class="ti ti-clock text-xs"></i>
                Queued — not in Plex yet
              </span>
            {/if}

            <!-- Always-visible link row -->
            <div class="flex items-center gap-2 flex-wrap">
              <!-- Watch on Plex — shown whenever in library -->
              {#if inLibrary}
                <Button icon="player-play" label="Watch on Plex" href={plexSearchUrl} external={true} />
              {/if}

              <!-- Always: View in Radarr / Sonarr -->
              <Button icon="external-link" label="View in {serviceLabel}" href={serviceUrl} external={true} />
            </div>

            <!-- Request flow — only when not already in library/queue -->
            {#if !inLibrary && !inQueue}
              {#if requestState === 'idle'}
                <button
                  onclick={openRequestPanel}
                  class="cursor-pointer font-mono text-xs font-black px-4 py-2 rounded-sm
                         bg-zinc-900 border border-white/20 text-gray-200
                         hover:bg-zinc-800 transition-colors"
                >
                  Request
                </button>

              {:else if requestState === 'selecting'}
                {#if profiles}
                  <div class="space-y-2">
                    <div class="flex items-center gap-2">
                      <label for="qp" class="font-mono text-xs text-gray-500 w-20 shrink-0">Quality</label>
                      <select id="qp" bind:value={selectedQP}
                        class="flex-1 font-mono text-xs bg-zinc-900 border border-white/10 rounded-md
                               px-2 py-1.5 text-gray-200 focus:outline-none focus:border-white/30">
                        {#each profiles.quality_profiles as qp}
                          <option value={qp.id}>{qp.name}</option>
                        {/each}
                      </select>
                    </div>
                    <div class="flex items-center gap-2">
                      <label for="rf" class="font-mono text-xs text-gray-500 w-20 shrink-0">Folder</label>
                      <select id="rf" bind:value={selectedRoot}
                        class="flex-1 font-mono text-xs bg-zinc-900 border border-white/10 rounded-md
                               px-2 py-1.5 text-gray-200 focus:outline-none focus:border-white/30">
                        {#each profiles.root_folders as f}
                          <option value={f.path}>{f.path}</option>
                        {/each}
                      </select>
                    </div>
                    <button onclick={confirmRequest}
                      class="cursor-pointer font-mono text-xs font-black px-4 py-2 rounded-md
                             bg-blue-500/20 border border-blue-500/30 text-blue-300
                             hover:bg-blue-500/30 transition-colors">
                      Confirm Request
                    </button>
                  </div>
                {:else}
                  <p class="font-mono text-xs text-gray-500">Loading profiles…</p>
                {/if}

              {:else if requestState === 'loading'}
                <span class="font-mono text-xs text-gray-400 flex items-center gap-2">
                  <i class="ti ti-loader-2 animate-spin text-sm"></i>
                  Sending request…
                </span>

              {:else if requestState === 'done'}
                <span class="inline-flex items-center gap-1.5 font-mono text-xs text-green-400
                             bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-md">
                  <i class="ti ti-check text-xs"></i>
                  Requested — downloading soon
                </span>

              {:else if requestState === 'exists'}
                <span class="inline-flex items-center gap-1.5 font-mono text-xs text-yellow-400
                             bg-yellow-500/10 border border-yellow-500/20 px-3 py-1.5 rounded-md">
                  <i class="ti ti-alert-triangle text-xs"></i>
                  Already in {serviceLabel}
                </span>

              {:else if requestState === 'error'}
                <span class="inline-flex items-center gap-1.5 font-mono text-xs text-red-400
                             bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-md">
                  <i class="ti ti-x text-xs"></i>
                  {errorMsg}
                </span>
              {/if}
            {/if}

            <!-- ── Delete (only when we have a library ID) ────────────── -->
            {#if deletableId}
              <div class="pt-2 border-t border-white/5">
                {#if deleteState === 'idle' || deleteState === 'error'}
                  <button
                    onclick={() => { deleteState = 'confirm'; deleteError = ''; }}
                    class="cursor-pointer flex items-center gap-1.5 font-mono text-xs
                           text-red-500/70 hover:text-red-400 transition-colors"
                  >
                    <i class="ti ti-trash text-xs"></i>
                    Delete from library
                  </button>
                  {#if deleteState === 'error'}
                    <p class="font-mono text-xs text-red-400 mt-1">{deleteError}</p>
                  {/if}

                {:else if deleteState === 'confirm'}
                  <div class="rounded-md border border-red-500/20 bg-red-500/5 p-3 space-y-2">
                    <p class="font-mono text-xs text-red-400">
                      Delete <span class="text-white font-bold">"{result.title}"</span>
                      from disk? This cannot be undone.
                    </p>
                    <div class="flex items-center gap-2">
                      <button onclick={confirmDelete}
                        class="cursor-pointer font-mono text-xs px-3 py-1.5 rounded-md
                               bg-red-500/20 border border-red-500/30 text-red-400
                               hover:bg-red-500/30 transition-colors flex items-center gap-1.5">
                        <i class="ti ti-trash text-xs"></i>
                        Yes, delete
                      </button>
                      <button onclick={() => (deleteState = 'idle')}
                        class="cursor-pointer font-mono text-xs px-3 py-1.5 rounded-md
                               bg-white/5 border border-white/10 text-gray-400
                               hover:bg-white/10 transition-colors">
                        Cancel
                      </button>
                    </div>
                  </div>

                {:else if deleteState === 'deleting'}
                  <span class="font-mono text-xs text-gray-500 flex items-center gap-2">
                    <i class="ti ti-loader-2 animate-spin text-sm"></i>
                    Deleting…
                  </span>
                {/if}
              </div>
            {/if}

          </div>
        </div>
      </div>
    </div>
  </div>
</div>