<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { deleteMedia, formatBytes, fetchStatus, fetchDownloads, fetchQueue } from '$lib/api';
	import type { StatusData, MediaItem, Download, QueueData } from '$lib/types.d.ts';
	import DownloadCard from '$lib/components/DownloadCard.svelte';
	import QueueCard from '$lib/components/QueueCard.svelte';
	import InteractionBar from '@/components/InteractionBar.svelte';

	// ─── State ────────────────────────────────────────────────────────────────
	const tabs = [
		{ value: 'downloads', label: 'Downloads' },
		{ value: 'queue', label: 'Queue' },
		{ value: 'library', label: 'Library' }
	];
	let tab = $derived<'downloads' | 'queue' | 'library'>(
		(() => {
			const t = $page.url.searchParams.get('tab');
			return (t === 'downloads' || t === 'queue' || t === 'library') ? t : 'downloads';
		})()
	);
	let status = $state<StatusData | null>(null);
	let downloads = $state<Download[]>([]);
	let queue = $state<QueueData>({ movies: [], series: [] });
	let loading = $state(true);
	let error = $state('');

	let search = $state('');
	let sortBy = $state<'title' | 'size' | 'progress'>('progress');
	let sortAsc = $state(false);

	let confirmDelete = $state<MediaItem | null>(null);
	let deleting = $state(false);
	let deleteError = $state('');
	let deleteSuccess = $state('');
	let refreshing = $state(false);

	// ─── Derived ──────────────────────────────────────────────────────────────
	let allMedia = $derived<MediaItem[]>(
		status
			? [
					...status.movies.map((m) => ({ ...m, type: 'movie' as const })),
					...status.series.map((s) => ({ ...s, type: 'series' as const }))
				]
			: []
	);

	let filtered = $derived(
		allMedia
			.filter((m) => {
				if (search && !m.title.toLowerCase().includes(search.toLowerCase())) return false;
				return true;
			})
			.sort((a, b) => {
				let cmp = 0;
				if (sortBy === 'title') cmp = a.title.localeCompare(b.title);
				else if (sortBy === 'size') cmp = a.size_gb - b.size_gb;
				return sortAsc ? cmp : -cmp;
			})
	);

	let totalSize = $derived(allMedia.reduce((s, m) => s + (m.size_gb ?? 0), 0));
	let totalDownloadSize = $derived(downloads.reduce((s, d) => s + d.size_gb, 0));

	// for delete modal
	function portal(node: HTMLElement) {
		document.body.appendChild(node);
		return {
			destroy() {
				node.remove();
			}
		};
	}

	// ─── Load ─────────────────────────────────────────────────────────────────
	async function loadData() {
		loading = true;
		error = '';
		try {
			const [statusResp, downloadsResp, queueResp] = await Promise.all([
				fetchStatus(),
				fetchDownloads(),
				fetchQueue()
			]);
			status = statusResp;
			downloads = downloadsResp;
			queue = queueResp;
		} catch (e) {
			error = 'Failed to load data';
			console.error(e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});

	// ─── Delete ───────────────────────────────────────────────────────────────
	async function handleDelete() {
		if (!confirmDelete) return;
		deleting = true;
		deleteError = '';
		deleteSuccess = '';
		try {
			await deleteMedia(confirmDelete.id, confirmDelete.type);
			deleteSuccess = `"${confirmDelete.title}" deleted.`;
			if (status) {
				status = {
					...status,
					movies: status.movies.filter((m) => m.id !== confirmDelete!.id),
					series: status.series.filter((s) => s.id !== confirmDelete!.id)
				};
			}
			confirmDelete = null;
		} catch {
			deleteError = 'Delete failed. Check the API.';
		} finally {
			deleting = false;
		}
	}

	function sortToggle(col: typeof sortBy) {
		if (sortBy === col) sortAsc = !sortAsc;
		else {
			sortBy = col;
			sortAsc = false;
		}
	}

	const sectionClass =
		'font-mono text-xs font-bold tracking-widest uppercase text-gray-500 flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10 mb-4';
	</script>

	<InteractionBar {tabs} {tab} loadData={loadData} paramKey="tab" />
	
{#if error}
	<div
		class="mb-4 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-3"
	>
		<i class="ti ti-alert-circle text-sm text-red-400"></i>
		<span class="font-mono text-xs text-red-400">{error}</span>
	</div>
{/if}

<!-- ─── Downloads Tab ────────────────────────────────────────────────────── -->
{#if tab === 'downloads'}
	<section>
		<h2 class={sectionClass}>
			<i class="ti ti-download text-xs"></i>
			Active Downloads
		</h2>

		{#if loading}
			<div class="space-y-3">
				{#each Array(3) as _, i (i)}
					<div id={_} class="h-24 animate-pulse rounded-lg bg-white/5"></div>
				{/each}
			</div>
		{:else if downloads.length > 0}
			<div class="space-y-3">
				{#each downloads as download (download.name)}
					<!-- ensure DownloadCard receives full Download shape by filling missing fields -->
					<DownloadCard
						download={{
							...download,
							progress: download.progress ?? 0,
							speed_mb: download.speed_mb ?? 0,
							eta: String(download.eta ?? 0),
							state: download.state ?? 'pending'
						}}
					/>
				{/each}
			</div>
			<p class="mt-4 font-mono text-xs text-gray-600">
				Total: {formatBytes(totalDownloadSize * 1024 ** 3)}
			</p>
		{:else}
			<p class="font-mono text-xs text-gray-600">No active downloads</p>
		{/if}
	</section>

	<!-- ─── Queue Tab ──────────────────────────────────────────────────────── -->
{:else if tab === 'queue'}
	<section>
		<h2 class={sectionClass}>
			<i class="ti ti-inbox text-xs"></i>
			Download Queue
		</h2>

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
							{#each queue.movies as item (item.id)}
								<QueueCard {item} type="movie" />
							{/each}
						</div>
					</div>
				{/if}

				{#if queue.series.length > 0}
					<div>
						<p class="mb-2 font-mono text-xs text-gray-500">Series ({queue.series.length})</p>
						<div class="space-y-2">
							{#each queue.series as item (item.id)}
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

	<!-- ─── Library Tab ──────────────────────────────────────────────────────── -->
{:else if tab === 'library'}
	<section>
		<h2 class={sectionClass}>
			<i class="ti ti-movie text-xs"></i>
			Library
		</h2>

		<!-- Toolbar -->
		<div class="mb-4 flex flex-wrap items-center gap-3">
			<!-- Search -->
			<div
				class="flex min-w-48 flex-1 items-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 py-2"
			>
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

			<!-- Count -->
			<div class="flex items-center gap-4">
				<span class="font-mono text-xs text-gray-600">{filtered.length} items</span>
				<span class="font-mono text-xs text-gray-500"
					>Total: {formatBytes(totalSize * 1024 ** 3)}</span
				>
			</div>
		</div>

		<!-- Success / error flash -->
		{#if deleteSuccess}
			<div
				class="mb-3 flex items-center gap-2 rounded-md border border-green-500/30 bg-green-500/10 px-4 py-2"
			>
				<i class="ti ti-check text-sm text-green-400"></i>
				<span class="font-mono text-xs text-green-400">{deleteSuccess}</span>
			</div>
		{/if}
		{#if deleteError}
			<div
				class="mb-3 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-2"
			>
				<i class="ti ti-alert-circle text-sm text-red-400"></i>
				<span class="font-mono text-xs text-red-400">{deleteError}</span>
			</div>
		{/if}

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
							<!-- Title -->
							<div class="flex min-w-0 items-center gap-2">
								<i
									class="ti ti-{item.type === 'movie'
										? 'movie'
										: 'device-tv'} shrink-0 text-xs text-gray-600"
								></i>
								<span class="truncate font-mono text-xs text-gray-200">{item.title}</span>
							</div>
							<!-- Size -->
							<span class="font-mono text-xs text-gray-400"
								>{formatBytes(item.size_gb * 1024 ** 3, 1)}</span
							>
							<!-- Type -->
							<span class="font-mono text-xs text-gray-500 capitalize">{item.type}</span>
							<!-- Added -->
							<span class="font-mono text-xs text-gray-500">{item.added ?? '—'}</span>
							<!-- Delete -->
							<button
								onclick={() => {
									confirmDelete = item;
									deleteSuccess = '';
									deleteError = '';
								}}
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
{/if}

<!-- ─── Delete confirmation modal ─────────────────────────────────────────── -->
{#if confirmDelete}
	<div
		use:portal
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
		role="dialog"
		aria-modal="true"
	>
		<div class="w-full max-w-md space-y-5 rounded-xl border border-white/20 bg-[#0f1215] p-6">
			<div class="flex items-start gap-3">
				<div
					class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-red-500/20 bg-red-500/10"
				>
					<i class="ti ti-trash text-red-400"></i>
				</div>
				<div>
					<p class="font-mono text-sm font-bold text-gray-200">Delete media?</p>
					<p class="mt-1 font-mono text-xs text-gray-500">
						This will remove <span class="text-gray-200">"{confirmDelete.title}"</span>
						({formatBytes(confirmDelete.size_gb * 1024 ** 3)}) from your library. This cannot be
						undone.
					</p>
				</div>
			</div>

			{#if deleteError}
				<p class="font-mono text-xs text-red-400">{deleteError}</p>
			{/if}

			<div class="flex justify-end gap-3">
				<button
					onclick={() => {
						confirmDelete = null;
						deleteError = '';
					}}
					disabled={deleting}
					class="rounded-md border border-white/10 bg-white/5 px-4 py-2 font-mono text-xs
					       text-gray-300 transition-all hover:bg-white/10 disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					onclick={handleDelete}
					disabled={deleting}
					class="flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/20 px-4
					       py-2 font-mono text-xs text-red-400 transition-all hover:bg-red-500/30 disabled:opacity-50"
				>
					{#if deleting}
						<i class="ti ti-loader-2 animate-spin text-sm"></i>
					{:else}
						<i class="ti ti-trash text-sm"></i>
					{/if}
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}
