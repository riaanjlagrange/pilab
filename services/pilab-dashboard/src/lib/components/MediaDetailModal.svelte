<script lang="ts">
    import type { SearchResult, ServiceProfiles, RequestPayload } from '$lib/types.d.ts';
    import { getRadarrProfiles, getSonarrProfiles, requestMovie, requestShow } from '$lib/api';
    import { env } from '$env/dynamic/public';
    import Button from './Button.svelte';

    let { result, onclose }: {
        result:  SearchResult;
        onclose: () => void;
    } = $props();

    type RequestState = 'idle' | 'selecting' | 'loading' | 'done' | 'exists' | 'error';

    let requestState  = $state<RequestState>('idle');
    let profiles      = $state<ServiceProfiles | null>(null);
    let selectedQP    = $state<number | null>(null);
    let selectedRoot  = $state<string | null>(null);
    let errorMsg      = $state('');

    // in_plex = actually streamable on Plex right now
    // in_radarr/in_sonarr = monitored/queued but may not be available yet
    let inPlex    = $derived(result.in_plex ?? result.source == 'plex');
    let inQueue   = $derived(!inPlex && ((result.in_radarr ?? false) || (result.in_sonarr ?? false)));

    async function openRequestPanel() {
        requestState = 'selecting';
        const data   = result.type === 'movie'
        ? await getRadarrProfiles()
        : await getSonarrProfiles();
        profiles     = data;
        selectedQP   = data.quality_profiles[0]?.id  ?? null;
        selectedRoot = data.root_folders[0]?.path     ?? null;
    }

    async function confirmRequest() {
        if (!selectedQP || !selectedRoot) return;
        requestState = 'loading';

        const payload: RequestPayload = {
        quality_profile_id: selectedQP,
        root_folder:        selectedRoot,
        };
        if (result.type === 'movie') payload.tmdb_id = result.tmdb_id;
        else                         payload.tvdb_id = result.tvdb_id;

        const res = result.type === 'movie'
        ? await requestMovie(payload)
        : await requestShow(payload);

        if (res.ok)                              requestState = 'done';
        else if (res.error === 'already_exists') requestState = 'exists';
        else { requestState = 'error'; errorMsg = res.error ?? 'Unknown error'; }
    }

    function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onclose();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- Backdrop -->
<div
  class="fixed inset-0 z-60 bg-black/70 flex items-center justify-center p-4"
  role="button"
  tabindex="0"
  onclick={onclose}
  aria-label="Close modal"
  title="Close modal"
  onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') onclose(); }}
>
  <!-- Modal -->
  <div
    class="flex flex-col justify-between relative w-[50%] h-[60vh] bg-[#111] border border-white/10
           rounded-xl overflow-hidden shadow-2xl"
    role="button"
    tabindex="0"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => { if (e.key !== 'Escape') e.stopPropagation(); }}
    aria-label="Media details dialog"
    title="Media details dialog"
  >
    <!-- Fanart banner -->
    {#if result.fanart_url}
      <div class="h-72 w-full overflow-hidden relative">
        <img src={result.fanart_url} alt="" class="w-full h-full object-cover opacity-40" />
        <div class="absolute inset-0 bg-gradient-to-b from-transparent to-[#111]"></div>
      </div>
    {:else}
      <div class="h-8"></div>
    {/if}

    <!-- Close -->
    <button
      onclick={onclose}
      class="cursor-pointer absolute top-3 right-3 text-white hover:text-gray-200 transition-colors"
      aria-label="Close"
      title="Close"
    >
      <i class="ti ti-x text-lg"></i>
    </button>

    <div
      class="flex gap-5 px-6 pb-12 justify-center items-end"
      class:pt-0={result.fanart_url}
      class:pt-4={!result.fanart_url}
    >
      <!-- Poster -->
      <div class="shrink-0 w-36 h-52 -mt-12 rounded-lg overflow-hidden border border-white/10
                  shadow-xl bg-white/5 flex items-center justify-center aspect-[2/3]">
        {#if result.poster_url}
          <img src={result.poster_url} alt={result.title} class="w-full h-full object-cover z-100" />
        {:else}
          <i class="ti ti-{result.type === 'show' ? 'device-tv' : 'movie'} text-gray-600 text-3xl"></i>
        {/if}
      </div>

      <!-- Details -->
      <div class="flex-1 min-w-0 pt-2">
        <div class="flex items-start gap-2 flex-wrap">
          <h2 class="font-mono font-bold text-gray-100 text-lg leading-tight">{result.title}</h2>
          {#if result.year}
            <span class="font-mono text-sm text-gray-500 mt-0.5">{result.year}</span>
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
          <span class="font-mono text-[10px] px-1.5 py-0.5 rounded
                       {result.type === 'show'
                         ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                         : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'}">
            {result.type}
          </span>
        </div>

        <!-- Overview -->
        {#if result.overview}
          <p class="font-mono text-xs text-gray-400 leading-relaxed mt-3 line-clamp-4">
            {result.overview}
          </p>
        {/if}

        <!-- Request section -->
        <div class="mt-4">

          {#if inPlex}
            <!-- Already streamable on Plex -->
            <div class="flex items-center gap-2 flex-wrap">
              <span class="inline-flex items-center gap-1.5 font-mono text-xs text-green-400
                           bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-md">
                <i class="ti ti-check text-xs"></i>
                Already in library
              </span>
              <Button icon="external-link" label="Watch on Plex" href={result.plex_link} external={true} />
            </div>

          {:else if inQueue}
            <!-- In Radarr/Sonarr but not on Plex yet -->
            <div class="flex items-center gap-2 flex-wrap">
              <span class="inline-flex items-center gap-1.5 font-mono text-xs text-yellow-400
                           bg-yellow-500/10 border border-yellow-500/20 px-3 py-1.5 rounded-md">
                <i class="ti ti-clock text-xs"></i>
                Already queued
              </span>
              {#if result.type === 'movie'}
                <Button icon="list-check" label="View on Radarr" href={`http://${env.PUBLIC_HOST}:7878`} external={true} />
              {:else}
                <Button icon="list-check" label="View on Sonarr" href={`http://${env.PUBLIC_HOST}:8989`} external={true} />
              {/if}
            </div>

          {:else if requestState === 'idle'}
            <button
              onclick={openRequestPanel}
              class="cursor-pointer font-mono text-xs font-black px-4 py-2 rounded-sm
                     bg-zinc-900 border border-white/20 text-gray-200 hover:bg-zinc-800 transition-colors"
            >
              Request
            </button>

          {:else if requestState === 'selecting'}
            {#if profiles}
              <div class="space-y-2.5">
                <div class="flex items-center gap-2">
                  <label for="quality-profile" class="font-mono text-xs text-gray-500 w-28 shrink-0">
                    Quality
                  </label>
                  <select
                    id="quality-profile"
                    bind:value={selectedQP}
                    class="flex-1 font-mono text-xs bg-zinc-900 border border-white/10 rounded-md
                           px-2 py-1.5 text-gray-200 focus:outline-none focus:border-white/30"
                  >
                    {#each profiles.quality_profiles as qp}
                      <option value={qp.id}>{qp.name}</option>
                    {/each}
                  </select>
                </div>

                <div class="flex items-center gap-2">
                  <label for="root-folder" class="font-mono text-xs text-gray-500 w-28 shrink-0">
                    Folder
                  </label>
                  <select
                    id="root-folder"
                    bind:value={selectedRoot}
                    class="flex-1 font-mono text-xs bg-zinc-900 border border-white/10 rounded-sm
                           px-2 py-1.5 text-gray-200 focus:outline-none focus:border-white/30"
                  >
                    {#each profiles.root_folders as f}
                      <option value={f.path}>{f.path}</option>
                    {/each}
                  </select>
                </div>

                <button
                  onclick={confirmRequest}
                  class="cursor-pointer font-mono text-xs font-black px-4 py-2 rounded-md
                         bg-blue-500/20 border border-blue-500/30 text-blue-300
                         hover:bg-blue-500/30 transition-colors"
                >
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
            <div class="flex items-center gap-2 flex-wrap">
              <span class="inline-flex items-center gap-1.5 font-mono text-xs text-green-400
                           bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-md">
                <i class="ti ti-check text-xs"></i>
                Requested — downloading soon
              </span>
              {#if result.type === 'movie'}
                <Button icon="list-check" label="View on Radarr" href={`http://${env.PUBLIC_HOST}:7878`} external={true} />
              {:else}
                <Button icon="list-check" label="View on Sonarr" href={`http://${env.PUBLIC_HOST}:8989`} external={true} />
              {/if}
              <Button icon="download" label="Go To Downloads" href="/manager" />
            </div>

          {:else if requestState === 'exists'}
            <span class="inline-flex items-center gap-1.5 font-mono text-xs text-yellow-400
                         bg-yellow-500/10 border border-yellow-500/20 px-3 py-1.5 rounded-md">
              <i class="ti ti-alert-triangle text-xs"></i>
              Already in Radarr/Sonarr
            </span>

          {:else if requestState === 'error'}
            <span class="inline-flex items-center gap-1.5 font-mono text-xs text-red-400
                         bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-md">
              <i class="ti ti-x text-xs"></i>
              {errorMsg}
            </span>
          {/if}

        </div>
      </div>
    </div>
  </div>
</div>