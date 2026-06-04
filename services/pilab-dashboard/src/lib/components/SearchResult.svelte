<script lang="ts">
  import type { SearchResult } from '$lib/types.d.ts';

  let { result, onclick }: {
    result:  SearchResult;
    onclick: (r: SearchResult) => void;
  } = $props();

  let badge = $derived(
    (result.in_plex || result.source === 'plex') ? 'In Library' :
    ((result.in_radarr ?? false) || (result.in_sonarr ?? false)) ? 'In Queue' :
    null
  );

  let badgeColor = $derived(
    badge === 'In Library'
      ? 'bg-green-500/20 text-green-400 border-green-500/30'
      : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
  );

  // Normalize 'series' → 'show' for display since Sonarr returns 'series'
  // but the type badge reads better as 'show'
  let typeLabel = $derived(
    result.type === 'series' ? 'show' : result.type
  );
</script>

<button
  onclick={() => onclick(result)}
  class="cursor-pointer w-full flex items-center gap-3 px-3 py-2.5 rounded-md
         hover:bg-white/10 transition-colors duration-150 text-left group"
>
  <div class="h-14 w-10 shrink-0 rounded overflow-hidden bg-white/5 border border-white/10
              flex items-center justify-center">
    {#if result.poster_url}
      <img src={result.poster_url} alt={result.title} class="h-full w-full object-cover" />
    {:else}
      <i class="ti ti-{result.type === 'show' || result.type === 'series' ? 'device-tv' : 'movie'} text-gray-600"></i>
    {/if}
  </div>

  <div class="min-w-0 flex-1">
    <div class="flex items-center gap-2">
      <p class="font-mono text-sm font-bold text-gray-200 truncate">{result.title}</p>
      {#if result.year}
        <span class="font-mono text-xs text-gray-600 shrink-0">{result.year}</span>
      {/if}
    </div>
    {#if result.overview}
      <p class="font-mono text-xs text-gray-600 truncate mt-0.5">{result.overview}</p>
    {/if}
  </div>

  <div class="shrink-0 flex flex-col items-end gap-1">
    {#if badge}
      <span class="font-mono text-[10px] px-1.5 py-0.5 rounded border {badgeColor}">
        {badge}
      </span>
    {/if}
    <span class="font-mono text-[10px] px-1.5 py-0.5 rounded border
                 {result.type === 'show' || result.type === 'series'
                   ? 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                   : 'bg-blue-500/20 text-blue-400 border-blue-500/30'}">
      {typeLabel}
    </span>
  </div>
</button>