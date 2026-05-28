<script lang="ts">
	interface Download {
		name: string;
		progress: number;
		speed_mb: number;
		eta: string;
		size_gb: number;
		state: string;
	}

	let { download }: { download: Download } = $props();

	let stateColor = $derived(
		download.state === 'downloading' ? 'text-blue-400' :
		download.state === 'metaDL' ? 'text-yellow-400' :
		'text-gray-400'
	);
</script>

<div class="rounded-lg bg-white/5 border border-white/10 p-4 space-y-3">
	<!-- Header -->
	<div class="flex items-start justify-between gap-3 min-w-0">
		<div class="min-w-0 flex-1">
			<p class="font-mono text-xs font-bold text-gray-200 truncate">{download.name}</p>
			<p class="font-mono text-xs {stateColor} mt-0.5">{download.state}</p>
		</div>
		<div class="text-right shrink-0">
			<p class="font-mono text-xs font-bold text-gray-200">{download.size_gb} GB</p>
		</div>
	</div>

	<!-- Progress bar -->
	<div class="space-y-1">
		<div class="flex justify-between font-mono text-xs text-gray-500">
			<span>{download.progress.toFixed(1)}%</span>
			<span>{download.speed_mb} MB/s</span>
		</div>
		<div class="h-2 w-full rounded-full bg-white/10 overflow-hidden">
			<div
				class="h-full rounded-full bg-blue-400 transition-all duration-300"
				style="width: {download.progress}%"
			></div>
		</div>
	</div>

	<!-- ETA -->
	<div class="flex justify-between items-center">
		<span class="font-mono text-xs text-gray-600">ETA</span>
		<span class="font-mono text-xs font-bold text-gray-300">{download.eta}</span>
	</div>
</div>
