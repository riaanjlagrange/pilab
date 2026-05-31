<script lang="ts">
	import type { QueueItem } from '$lib/types';
	let { item, type }: { item: QueueItem; type: 'movie' | 'series' } = $props();

	let statusColor = $derived(
		item.status === 'downloading'  ? 'text-blue-400'   :
		item.status === 'stalledDL'    ? 'text-yellow-400' :
		item.status === 'pausedDL'     ? 'text-gray-500'   :
		item.status === 'completed'    ? 'text-green-400'  :
		item.status === 'uploading'    ? 'text-purple-400' :
		item.status === 'failed'       ? 'text-red-400'    :
		'text-yellow-400'
	);

	let statusLabel = $derived(
		item.status === 'downloading'  ? 'downloading'  :
		item.status === 'stalledDL'    ? 'stalled'      :
		item.status === 'pausedDL'     ? 'paused'       :
		item.status === 'forcedDL'     ? 'forced'       :
		item.status === 'metaDL'       ? 'fetching meta':
		item.status === 'uploading'    ? 'seeding'      :
		item.status === 'completed'    ? 'complete'     :
		item.status
	);

	let addedDate = $derived(
		item.added_on ? new Date(item.added_on * 1000).toLocaleDateString() : null
	);
</script>

<div class="rounded-md bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-200 p-3 space-y-2">

	<!-- Row 1: Icon + Title + Progress -->
	<div class="flex items-center justify-between gap-3">
		<div class="flex items-center gap-3 min-w-0">
			<i class="ti ti-{type === 'series' ? 'device-tv' : 'movie'} text-gray-600 text-sm shrink-0"></i>
			<div class="min-w-0">
				<p class="font-mono text-xs font-bold text-gray-200 truncate">{item.title}</p>
				<p class="font-mono text-xs {statusColor} mt-0.5">{statusLabel}</p>
			</div>
		</div>
		<div class="text-right shrink-0">
			<p class="font-mono text-xs font-bold text-gray-300">{item.progress.toFixed(1)}%</p>
			<div class="h-1 w-20 rounded-full bg-white/10 mt-1 overflow-hidden">
				<div class="h-full rounded-full bg-blue-400 transition-all duration-500" style="width: {item.progress}%"></div>
			</div>
		</div>
	</div>

	<!-- Row 2: Speed + ETA + Size + Seeds/Peers -->
	<div class="flex items-center gap-3 flex-wrap">
		{#if item.speed_mb > 0}
			<span class="font-mono text-xs text-blue-400">
				<i class="ti ti-arrow-down text-[10px]"></i> {item.speed_mb} MB/s
			</span>
		{/if}
		{#if item.eta && item.eta !== 'unknown'}
			<span class="font-mono text-xs text-gray-500">
				<i class="ti ti-clock text-[10px]"></i> {item.eta}
			</span>
		{/if}
		{#if item.seeds > 0 || item.peers > 0}
			<span class="font-mono text-xs text-gray-600">
				<i class="ti ti-antenna-bars-4 text-[10px]"></i> {item.seeds}S {item.peers}P
			</span>
		{/if}
		{#if addedDate}
			<span class="font-mono text-xs text-gray-700">
				{addedDate}
			</span>
		{/if}
		{#if item.size_gb}
			<span class="font-mono text-xs text-gray-500 ml-auto">
				{item.completed_gb.toFixed(1)} / {item.size_gb.toFixed(1)} GB
			</span>
		{/if}
	</div>

</div>