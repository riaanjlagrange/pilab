<script lang="ts">
	interface QueueItem {
		title: string;
		status: string;
		progress: number;
	}

	let { item, type }: { item: QueueItem; type: 'movie' | 'series' } = $props();

	let statusColor = $derived(
		item.status === 'downloading' ? 'text-blue-400' :
		item.status === 'completed' ? 'text-green-400' :
		item.status === 'failed' ? 'text-red-400' :
		'text-yellow-400'
	);
</script>

<div class="flex items-center justify-between gap-3 rounded-md bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-200 p-3">
	<!-- Icon + Title -->
	<div class="flex items-center gap-3 min-w-0">
		<i class="ti ti-{type === 'series' ? 'device-tv' : 'movie'} text-gray-600 text-sm shrink-0"></i>
		<div class="min-w-0">
			<p class="font-mono text-xs font-bold text-gray-200 truncate">{item.title}</p>
			<p class="font-mono text-xs {statusColor} mt-0.5">{item.status}</p>
		</div>
	</div>

	<!-- Progress -->
	<div class="text-right shrink-0">
		<p class="font-mono text-xs font-bold text-gray-300">{item.progress.toFixed(1)}%</p>
		<div class="h-1 w-20 rounded-full bg-white/10 mt-1 overflow-hidden">
			<div
				class="h-full rounded-full bg-blue-400"
				style="width: {item.progress}%"
			></div>
		</div>
	</div>
</div>
