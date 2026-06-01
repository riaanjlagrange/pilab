<script lang="ts">
	import type { NowPlayingItem } from '$lib/types.d.ts';
	let { item }: { item: NowPlayingItem } = $props();
	let displayTitle = $derived(
		item.type === 'episode' && item.show
			? item.show
			: item.title
	);
	let subtitle = $derived(
		item.type === 'episode' && item.show
			? `${item.episode} · ${item.title}`
			: undefined
	);
	let stateIcon = $derived(
		item.state === 'paused' ? 'ti-player-pause' : 'ti-player-play'
	);
</script>

<a
	href={item.plex_link ?? '#'}
	target="_blank"
	rel="noopener noreferrer"
	class="flex rounded-sm gap-3 bg-white/5 border border-white/10 p-4
	       hover:bg-white/10 hover:border-white/20 transition-all duration-200"
>
	<div class="h-32 w-22 shrink-0 rounded-sm overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center">
		{#if item.thumb_url}
			<img src={item.thumb_url} alt={displayTitle} class="h-full w-full object-cover" />
		{:else}
			<i class="ti ti-{item.type === 'episode' ? 'device-tv' : 'movie'} text-gray-600 text-lg"></i>
		{/if}
	</div>
	<div class="flex flex-col gap-3 w-full">
		<div class="min-w-0 flex-1">
			<p class="font-mono text-sm font-bold text-gray-200 leading-tight">
				{displayTitle}
			</p>
			{#if subtitle}
				<p class="font-mono text-xs text-gray-500 truncate mt-0.5">{subtitle}</p>
			{/if}
			<div class="flex items-center gap-1.5 mt-1.5">
				<i class="ti ti-user text-gray-600 text-xs"></i>
				<span class="font-mono text-xs text-gray-500">{item.user}</span>
				<span class="mx-1 text-gray-700">·</span>
				<i class="ti {stateIcon} text-gray-600 text-xs"></i>
				<span class="font-mono text-xs text-gray-500 capitalize">{item.state}</span>
			</div>
		</div>
		<!-- Progress % -->
		<div class="shrink-0 font-mono text-xs text-blue-400 tabular-nums">
			{item.progress_pct ?? 0}%
		</div>
		<!-- Progress bar -->
		<div class="h-1 w-full rounded-full bg-white/10 overflow-hidden">
			<div
				class="h-full rounded-full bg-blue-400 transition-all duration-500"
				style="width: {item.progress_pct ?? 0}%"
			></div>
		</div>
	</div>
</a>