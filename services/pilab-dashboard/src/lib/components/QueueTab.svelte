<script lang="ts">
	import { env } from '$env/dynamic/public';
	import Button from '@/components/Button.svelte';
	import QueueCard from '$lib/components/QueueCard.svelte';
	import type { QueueData } from '$lib/types.d.ts';

	// ─── Props ────────────────────────────────────────────────────────────────
	let { queue, loading }: { queue: QueueData; loading: boolean } = $props();

	// ─── Derived ──────────────────────────────────────────────────────────────
	const statusPriority: Record<string, number> = {
		downloading: 0,
		forcedDL:    1,
		metaDL:      2,
		stalledDL:   3,
		pausedDL:    4,
		uploading:   5,
	};

	let sortedMovies = $derived(
		[...queue.movies].sort((a, b) => (statusPriority[a.status] ?? 9) - (statusPriority[b.status] ?? 9))
	);

	let sortedSeries = $derived(
		[...queue.series].sort((a, b) => (statusPriority[a.status] ?? 9) - (statusPriority[b.status] ?? 9))
	);
</script>

<section>
	<div class="flex items-center justify-between mb-4">
		<h2 class="font-mono text-xs font-bold tracking-widest uppercase text-gray-500 flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10 mb-4">
			<i class="ti ti-inbox text-xs"></i>
			Download Queue
		</h2>
		<Button icon="download" label="Manage on qBittorrent" href={`http://${env.PUBLIC_HOST}:8080`} external />
	</div>

	{#if loading}
		<div class="space-y-2">
			{#each Array(5) as _, i (i)}
				<div id={_} class="h-10 animate-pulse rounded bg-white/5"></div>
			{/each}
		</div>
	{:else if queue.movies.length > 0 || queue.series.length > 0}
		<div class="space-y-4">
			{#if queue.movies.length > 0}
				<div>
					<p class="mb-2 font-mono text-xs text-gray-500">Movies ({queue.movies.length})</p>
					<div class="space-y-2">
						{#each sortedMovies as item (item.id)}
							<QueueCard {item} type="movie" />
						{/each}
					</div>
				</div>
			{/if}

			{#if queue.series.length > 0}
				<div>
					<p class="mb-2 font-mono text-xs text-gray-500">Series ({queue.series.length})</p>
					<div class="space-y-2">
						{#each sortedSeries as item (item.id)}
							<QueueCard {item} type="series" />
						{/each}
					</div>
				</div>
			{/if}
		</div>
	{:else}
		<p class="font-mono text-xs text-gray-600">Queue is empty</p>
	{/if}
</section>