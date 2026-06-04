<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchDownloads, fetchQueue } from '$lib/api';
  import type { Download, QueueData } from '$lib/types.d.ts';

  // ─── State ──────────────────────────────────────────────────────────────
  let downloads = $state<Download[]>([]);
  let queue     = $state<QueueData>({ movies: [], series: [] });
  let loading   = $state(true);
  let error     = $state('');

  // ─── Derived ────────────────────────────────────────────────────────────
  let allQueue = $derived([...queue.movies, ...queue.series]);
  let totalActive = $derived(downloads.filter(d => d.status === 'downloading').length);

  // ─── Load ────────────────────────────────────────────────────────────────
  async function loadData(isBackground = false) {
    if (!isBackground) loading = true;
    error = '';
    try {
      const [dlRes, qRes] = await Promise.all([fetchDownloads(), fetchQueue()]);
      downloads = dlRes;
      queue     = qRes;
    } catch (e) {
      if (!isBackground) error = 'Failed to load downloads.';
      console.error(e);
    } finally {
      if (!isBackground) loading = false;
    }
  }

  onMount(() => {
    loadData();
    const interval = setInterval(() => loadData(true), 3000);
    return () => clearInterval(interval);
  });

  function speedColor(mbps: number) {
    if (mbps > 10) return 'text-green-400';
    if (mbps > 1)  return 'text-yellow-400';
    return 'text-gray-500';
  }

  function statusColor(status: string) {
    if (status === 'downloading') return 'text-green-400 bg-green-500/10 border-green-500/20';
    if (status === 'metaDL')     return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    return 'text-gray-400 bg-white/5 border-white/10';
  }
</script>

<!-- Header -->
<div class="flex items-center justify-between mb-6">
  <div>
    <h1 class="font-mono text-sm font-bold text-gray-200 flex items-center gap-2">
      <i class="ti ti-download text-[#e5a00d]"></i>
      Downloads
    </h1>
    {#if !loading}
      <p class="font-mono text-xs text-gray-600 mt-0.5">
        {totalActive} active · {allQueue.length} in queue
      </p>
    {/if}
  </div>
  <!-- live pulse -->
  {#if totalActive > 0}
    <span class="flex items-center gap-1.5 font-mono text-[10px] text-green-400">
      <span class="relative flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-green-400"></span>
      </span>
      Live
    </span>
  {/if}
</div>

{#if error}
  <div class="mb-4 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-3">
    <i class="ti ti-alert-circle text-sm text-red-400"></i>
    <span class="font-mono text-xs text-red-400">{error}</span>
  </div>
{/if}

<!-- ── Active torrents (qBittorrent) ─────────────────────────────────────── -->
<section class="mb-8">
  <p class="font-mono text-xs text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-3
            after:flex-1 after:h-px after:bg-white/10">
    Active Torrents
  </p>

  {#if loading}
    <div class="space-y-2">
      {#each Array(3) as _, i (i)}
        <div class="h-16 rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
      {/each}
    </div>
  {:else if downloads.length === 0}
    <div class="flex flex-col items-center justify-center py-12 text-center">
      <i class="ti ti-circle-check text-3xl text-gray-700 mb-2"></i>
      <p class="font-mono text-xs text-gray-600">Nothing downloading right now.</p>
    </div>
  {:else}
    <div class="space-y-2">
      {#each downloads as dl (dl.id)}
        <div class="rounded-lg border border-white/10 bg-white/[0.03] p-4">
          <div class="flex items-start justify-between gap-4 mb-2">
            <p class="font-mono text-xs text-gray-200 leading-snug line-clamp-2 flex-1">{dl.id}</p>
            <span class="shrink-0 font-mono text-[10px] px-1.5 py-0.5 rounded border {statusColor(dl.status)}">
              {dl.status}
            </span>
          </div>

          <!-- Progress bar -->
          <div class="h-1 w-full bg-white/10 rounded-full overflow-hidden mb-2">
            <div
              class="h-full rounded-full transition-all duration-1000
                     {dl.status === 'downloading' ? 'bg-[#e5a00d]' : 'bg-white/30'}"
              style="width: {dl.progress}%"
            ></div>
          </div>

          <div class="flex items-center justify-between font-mono text-[10px] text-gray-600">
            <span class="{speedColor(dl.speed_mb)}">
              {#if dl.speed_mb > 0}{dl.speed_mb.toFixed(1)} MB/s{:else}—{/if}
            </span>
            <span>{dl.progress.toFixed(1)}%</span>
            <span>{dl.size_gb.toFixed(2)} GB</span>
            <span>ETA {dl.eta || '—'}</span>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>

<!-- ── Radarr / Sonarr queue ──────────────────────────────────────────────── -->
<section>
  <p class="font-mono text-xs text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-3
            after:flex-1 after:h-px after:bg-white/10">
    Queue
  </p>

  {#if loading}
    <div class="space-y-2">
      {#each Array(4) as _, i (i)}
        <div class="h-14 rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
      {/each}
    </div>
  {:else if allQueue.length === 0}
    <div class="flex flex-col items-center justify-center py-12 text-center">
      <i class="ti ti-list-check text-3xl text-gray-700 mb-2"></i>
      <p class="font-mono text-xs text-gray-600">Queue is empty.</p>
    </div>
  {:else}
    <!-- Movies -->
    {#if queue.movies.length > 0}
      <p class="font-mono text-[10px] text-gray-600 uppercase tracking-widest mb-2 mt-1">Movies</p>
      <div class="space-y-1.5 mb-4">
        {#each queue.movies as item (item.id)}
          <div class="rounded-md border border-white/10 bg-white/[0.02] px-4 py-3">
            <div class="flex items-center justify-between gap-4">
              <p class="font-mono text-xs text-gray-300 flex-1 truncate">{item.title}</p>
              <span class="font-mono text-[10px] text-gray-600 shrink-0">{item.size_gb.toFixed(2)} GB</span>
              <span class="font-mono text-[10px] shrink-0 {statusColor(item.status)} px-1.5 py-0.5 rounded border">
                {item.status}
              </span>
            </div>
            {#if item.progress > 0}
              <div class="mt-2 h-0.5 w-full bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500/60 rounded-full" style="width: {item.progress}%"></div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}

    <!-- Series -->
    {#if queue.series.length > 0}
      <p class="font-mono text-[10px] text-gray-600 uppercase tracking-widest mb-2">Series</p>
      <div class="space-y-1.5">
        {#each queue.series as item (item.id)}
          <div class="rounded-md border border-white/10 bg-white/[0.02] px-4 py-3">
            <div class="flex items-center justify-between gap-4">
              <p class="font-mono text-xs text-gray-300 flex-1 truncate">{item.title}</p>
              <span class="font-mono text-[10px] text-gray-600 shrink-0">{item.size_gb.toFixed(2)} GB</span>
              <span class="font-mono text-[10px] shrink-0 {statusColor(item.status)} px-1.5 py-0.5 rounded border">
                {item.status}
              </span>
            </div>
            {#if item.progress > 0}
              <div class="mt-2 h-0.5 w-full bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-purple-500/60 rounded-full" style="width: {item.progress}%"></div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</section>