<script lang="ts">
	import type { OnDeckItem } from '$lib/types.d.ts';

	let { item }: { item: OnDeckItem } = $props();

	let displayTitle = $derived(
		item.type === 'episode' && item.grandparent_title
			? item.grandparent_title
			: item.title
	);

	let subtitle = $derived(
		item.type === 'episode' && item.grandparent_title ? item.title : (item.year?.toString() ?? '')
	);
</script>

<div class="flex items-center gap-3 rounded-md bg-white/5 border border-white/10
            hover:bg-white/10 hover:border-white/20 transition-all duration-200 p-3">
	<!-- Thumb -->
	<div class="h-10 w-16 shrink-0 rounded overflow-hidden bg-white/5 flex items-center justify-center">
		{#if item.thumb}
			<img src={item.thumb} alt={displayTitle} class="h-full w-full object-cover" />
		{:else}
			<i class="ti ti-movie text-gray-600 text-base"></i>
		{/if}
	</div>

	<div class="min-w-0">
		<p class="font-mono text-xs font-bold text-gray-200 truncate">{displayTitle}</p>
		{#if subtitle}
			<p class="font-mono text-xs text-gray-500 truncate mt-0.5">{subtitle}</p>
		{/if}
	</div>

	<div class="ml-auto shrink-0">
		<i class="ti ti-{item.type === 'episode' ? 'device-tv' : 'movie'} text-gray-600 text-sm"></i>
	</div>
</div>
