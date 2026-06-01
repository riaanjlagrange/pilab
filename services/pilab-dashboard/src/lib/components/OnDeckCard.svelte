<script lang="ts">
	import type { OnDeckItem } from '$lib/types.d.ts';
	let { item }: { item: OnDeckItem } = $props();
</script>

<a
	href={item.plex_link}
	target="_blank"
	rel="noopener noreferrer"
	class="relative block rounded-md overflow-hidden aspect-[2/3]
	       bg-white/5 border border-white/10 cursor-pointer group"
>
	<!-- Thumbnail -->
	<div class="w-full h-full">
		{#if item.thumb_url}
			<img src={item.thumb_url} alt={item.title} class="w-full h-full object-cover block" />
		{:else}
			<div class="w-full h-full flex items-center justify-center">
				<i class="ti ti-{item.type === 'episode' ? 'device-tv' : 'movie'} text-white/20 text-2xl"></i>
			</div>
		{/if}
	</div>

	<!-- Hover overlay -->
	<div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200
	            bg-gradient-to-t from-black/90 via-black/40 to-transparent
	            flex items-end">
		<div class="p-3 w-full">
			<i class="ti ti-player-play text-white text-xl mb-1 block"></i>
			<p class="font-mono text-[0.7rem] font-bold text-white leading-tight line-clamp-2 mb-1">
				{item.title}
			</p>
			{#if item.subtitle}
				<p class="font-mono text-[0.65rem] text-white/60 truncate mb-2">
					{item.subtitle}
				</p>
			{/if}
			{#if item.progress_pct}
				<div class="h-0.5 w-full bg-white/20 rounded-full overflow-hidden">
					<div class="h-full bg-[#e5a00d] rounded-full" style="width: {item.progress_pct}%"></div>
				</div>
			{/if}
		</div>
	</div>
</a>