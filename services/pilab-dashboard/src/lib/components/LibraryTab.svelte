<script lang="ts">
	import { formatBytes } from '$lib/api';
	import type { MediaItem } from '$lib/types.d.ts';

	// ─── Props ────────────────────────────────────────────────────────────────
	let {
		allMedia,
		loading,
		error,
		ondelete
	}: {
		allMedia: MediaItem[];
		loading: boolean;
		error: string;
		ondelete: (item: MediaItem) => void;
	} = $props();

	// ─── State ────────────────────────────────────────────────────────────────
	let search = $state('');
	let sortBy = $state<'title' | 'size'>('title');
	let sortAsc = $state(true);

	// ─── Derived ──────────────────────────────────────────────────────────────
	let filtered = $derived(
		allMedia
			.filter((m) => !search || m.title.toLowerCase().includes(search.toLowerCase()))
			.sort((a, b) => {
				const cmp =
					sortBy === 'title' ? a.title.localeCompare(b.title) : a.size_gb - b.size_gb;
				return sortAsc ? cmp : -cmp;
			})
	);

	let totalSize = $derived(allMedia.reduce((s, m) => s + (m.size_gb ?? 0), 0));

	// ─── Helpers ──────────────────────────────────────────────────────────────
	function sortToggle(col: typeof sortBy) {
		if (sortBy === col) sortAsc = !sortAsc;
		else { sortBy = col; sortAsc = false; }
	}
</script>

<section>
	<h2 class="font-mono text-xs font-bold tracking-widest uppercase text-gray-500 flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10 mb-4">
		<i class="ti ti-movie text-xs"></i>
		Library
	</h2>

	<!-- Toolbar -->
	<div class="mb-4 flex flex-wrap items-center gap-3">
		<div class="flex min-w-48 flex-1 items-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 py-2">
			<i class="ti ti-search text-sm text-gray-500"></i>
			<input
				type="text"
				placeholder="Search..."
				bind:value={search}
				class="w-full bg-transparent font-mono text-xs text-gray-200 placeholder-gray-600 outline-none"
			/>
			{#if search}
				<button
					title={search}
					onclick={() => (search = '')}
					class="text-gray-600 hover:text-gray-400"
				>
					<i class="ti ti-x text-xs"></i>
				</button>
			{/if}
		</div>

		<div class="flex items-center gap-4">
			<span class="font-mono text-xs text-gray-600">{filtered.length} items</span>
			<span class="font-mono text-xs text-gray-500">Total: {formatBytes(totalSize * 1024 ** 3)}</span>
		</div>
	</div>

	{#if loading}
		<div class="space-y-2">
			{#each Array(8) as _, i (i)}
				<div id={_} class="h-10 animate-pulse rounded bg-white/5"></div>
			{/each}
		</div>
	{:else if error}
		<p class="font-mono text-xs text-red-400">{error}</p>
	{:else}
		<!-- Table -->
		<div class="overflow-hidden rounded-lg border border-white/10">
			<!-- Header -->
			<div
				class="grid gap-2 border-b border-white/10 bg-white/5 px-4 py-2"
				style="grid-template-columns: 1fr 5rem 4rem 5rem 2.5rem"
			>
				{#each [['title', 'Title'], ['size', 'Size']] as [col, lbl] (col)}
					<button
						onclick={() => sortToggle(col as typeof sortBy)}
						class="flex items-center gap-1 text-left font-mono text-xs tracking-widest text-gray-500 uppercase transition-colors hover:text-gray-300"
					>
						{lbl}
						{#if sortBy === col}
							<i class="ti ti-chevron-{sortAsc ? 'up' : 'down'} text-xs text-blue-400"></i>
						{/if}
					</button>
				{/each}
				<span class="font-mono text-xs tracking-widest text-gray-500 uppercase">Type</span>
				<span class="font-mono text-xs tracking-widest text-gray-500 uppercase">Added</span>
				<span></span>
			</div>

			<!-- Rows -->
			<div class="divide-y divide-white/5">
				{#each filtered as item (item.title + item.type)}
					<div
						class="group grid items-center gap-2 px-4 py-2.5 transition-colors hover:bg-white/5"
						style="grid-template-columns: 1fr 5rem 4rem 5rem 2.5rem"
					>
						<div class="flex min-w-0 items-center gap-2">
							<i class="ti ti-{item.type === 'movie' ? 'movie' : 'device-tv'} shrink-0 text-xs text-gray-600"></i>
							<span class="truncate font-mono text-xs text-gray-200">{item.title}</span>
						</div>
						<span class="font-mono text-xs text-gray-400">{formatBytes(item.size_gb * 1024 ** 3, 1)}</span>
						<span class="font-mono text-xs text-gray-500 capitalize">{item.type}</span>
						<span class="font-mono text-xs text-gray-500">{item.added ?? '—'}</span>
						<button
							onclick={() => ondelete(item)}
							class="text-gray-700 opacity-0 transition-colors group-hover:opacity-100 hover:text-red-400"
							aria-label="Delete {item.title}"
						>
							<i class="ti ti-trash text-sm"></i>
						</button>
					</div>
				{/each}

				{#if filtered.length === 0}
					<div class="px-4 py-8 text-center font-mono text-xs text-gray-600">No media found.</div>
				{/if}
			</div>
		</div>
	{/if}
</section>