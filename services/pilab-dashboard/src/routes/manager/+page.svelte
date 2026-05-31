<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { deleteMedia, fetchStatus, fetchQueue, formatBytes } from '$lib/api';
	import type { StatusData, MediaItem, QueueData } from '$lib/types.d.ts';
	import InteractionBar from '@/components/InteractionBar.svelte';
	import QueueTab from '$lib/components/QueueTab.svelte';
	import LibraryTab from '$lib/components/LibraryTab.svelte';

	// ─── State ────────────────────────────────────────────────────────────────
	const tabs = [
		{ value: 'queue', label: 'Queue' },
		{ value: 'library', label: 'Library' }
	];
	let tab = $derived<'queue' | 'library'>(
		(() => {
			const t = $page.url.searchParams.get('tab');
			return (t === 'queue' || t === 'library') ? t : 'queue';
		})()
	);

	let status = $state<StatusData | null>(null);
	let queue = $state<QueueData>({ movies: [], series: [] });
	let loading = $state(true);
	let error = $state('');

	let confirmDelete = $state<MediaItem | null>(null);
	let deleting = $state(false);
	let deleteError = $state('');
	let deleteSuccess = $state('');

	// ─── Derived ──────────────────────────────────────────────────────────────
	let allMedia = $derived<MediaItem[]>(
		status
			? [
					...status.movies.map((m) => ({ ...m, type: 'movie' as const })),
					...status.series.map((s) => ({ ...s, type: 'series' as const }))
				]
			: []
	);

	// for delete modal
	function portal(node: HTMLElement) {
		document.body.appendChild(node);
		return { destroy() { node.remove(); } };
	}

	// ─── Load ─────────────────────────────────────────────────────────────────
	async function loadData(isBackground = false) {
		if (!isBackground) loading = true;
		error = '';
		try {
			const [statusResp, queueResp] = await Promise.all([fetchStatus(), fetchQueue()]);
			status = statusResp;
			queue = queueResp;
		} catch (e) {
			if (!isBackground) error = 'Failed to load data';
			console.error(e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
		const interval = setInterval(() => loadData(true), 2000);
		return () => clearInterval(interval);
	});

	// ─── Delete ───────────────────────────────────────────────────────────────
	function handleDeleteRequest(item: MediaItem) {
		confirmDelete = item;
		deleteSuccess = '';
		deleteError = '';
	}

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
</script>

<InteractionBar {tabs} {tab} loadData={loadData} paramKey="tab" />

{#if error}
	<div class="mb-4 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-3">
		<i class="ti ti-alert-circle text-sm text-red-400"></i>
		<span class="font-mono text-xs text-red-400">{error}</span>
	</div>
{/if}

<!-- Success / error flash (delete feedback) -->
{#if deleteSuccess}
	<div class="mb-3 flex items-center gap-2 rounded-md border border-green-500/30 bg-green-500/10 px-4 py-2">
		<i class="ti ti-check text-sm text-green-400"></i>
		<span class="font-mono text-xs text-green-400">{deleteSuccess}</span>
	</div>
{/if}
{#if deleteError && !confirmDelete}
	<div class="mb-3 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-2">
		<i class="ti ti-alert-circle text-sm text-red-400"></i>
		<span class="font-mono text-xs text-red-400">{deleteError}</span>
	</div>
{/if}

{#if tab === 'queue'}
	<QueueTab {queue} {loading} />
{:else if tab === 'library'}
	<LibraryTab {allMedia} {loading} {error} ondelete={handleDeleteRequest} />
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
				<div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-red-500/20 bg-red-500/10">
					<i class="ti ti-trash text-red-400"></i>
				</div>
				<div>
					<p class="font-mono text-sm font-bold text-gray-200">Delete media?</p>
					<p class="mt-1 font-mono text-xs text-gray-500">
						This will remove <span class="text-gray-200">"{confirmDelete.title}"</span>
						({formatBytes(confirmDelete.size_gb * 1024 ** 3)}) from your library. This cannot be undone.
					</p>
				</div>
			</div>

			{#if deleteError}
				<p class="font-mono text-xs text-red-400">{deleteError}</p>
			{/if}

			<div class="flex justify-end gap-3">
				<button
					onclick={() => { confirmDelete = null; deleteError = ''; }}
					disabled={deleting}
					class="rounded-md border border-white/10 bg-white/5 px-4 py-2 font-mono text-xs text-gray-300 transition-all hover:bg-white/10 disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					onclick={handleDelete}
					disabled={deleting}
					class="flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/20 px-4 py-2 font-mono text-xs text-red-400 transition-all hover:bg-red-500/30 disabled:opacity-50"
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