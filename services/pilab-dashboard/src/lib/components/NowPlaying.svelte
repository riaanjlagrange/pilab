<script lang="ts">
	import type { NowPlayingItem } from '$lib/types.d.ts';

	let { item }: { item: NowPlayingItem } = $props();

	let progress = $derived(
		item.duration > 0 ? Math.round((item.progress / item.duration) * 100) : 0
	);

	let displayTitle = $derived(
		item.type === 'episode' && item.grandparent_title
			? `${item.grandparent_title} — ${item.title}`
			: item.title
	);

	function fmtMs(ms: number): string {
		const s = Math.floor(ms / 1000);
		const h = Math.floor(s / 3600);
		const m = Math.floor((s % 3600) / 60);
		const sec = s % 60;
		if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
		return `${m}:${String(sec).padStart(2, '0')}`;
	}
</script>

<div class="rounded-lg bg-white/5 border border-white/10 p-4 space-y-3">
	<div class="flex items-start gap-3">
		<!-- Thumb placeholder / actual thumb -->
		<div class="h-12 w-20 shrink-0 rounded overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center">
			{#if item.thumb}
				<img src={item.thumb} alt={item.title} class="h-full w-full object-cover" />
			{:else}
				<i class="ti ti-movie text-gray-600 text-lg"></i>
			{/if}
		</div>

		<div class="min-w-0 flex-1">
			<p class="font-mono text-sm font-bold text-gray-200 leading-tight truncate">{displayTitle}</p>
			<div class="flex items-center gap-2 mt-1">
				<i class="ti ti-user text-xs text-gray-500"></i>
				<span class="font-mono text-xs text-gray-500">{item.user}</span>
				<span class="font-mono text-xs text-blue-400 ml-auto">{progress}%</span>
			</div>
		</div>
	</div>

	<!-- Progress bar -->
	<div class="space-y-1">
		<div class="h-1 w-full rounded-full bg-white/10 overflow-hidden">
			<div
				class="h-full rounded-full bg-blue-400 transition-all duration-500"
				style="width: {progress}%"
			></div>
		</div>
		<div class="flex justify-between">
			<span class="font-mono text-xs text-gray-600">{fmtMs(item.progress)}</span>
			<span class="font-mono text-xs text-gray-600">{fmtMs(item.duration)}</span>
		</div>
	</div>
</div>
