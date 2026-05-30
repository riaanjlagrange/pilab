<script lang="ts">
	import { onMount } from 'svelte';
	import { replaceState } from '$app/navigation';
	import { page } from '$app/stores';
	import { fetchContainers } from '$lib/api';
	import { CONTAINER_META, CATEGORY_ORDER, CATEGORY_LABELS, type ContainerCategory } from '$lib/config';
	import type { Container } from '$lib/types.d.ts';
	import ContainerCard from '$lib/components/ContainerCard.svelte';
	import FilterControl from '$lib/components/FilterControl.svelte';
	import InteractionBar from '@/components/InteractionBar.svelte';

	// ─── State ────────────────────────────────────────────────────────────────

	let containers = $state<Container[]>([]);
	let loading = $state(true);
	let error = $state('');
	const filters = [
		{ value: 'all', label: 'All' },
		{ value: 'running', label: 'Running' },
		{ value: 'stopped', label: 'Stopped' }
	];
	let filter = $derived<'all' | 'running' | 'stopped'>(
		(() => {
			const t = $page.url.searchParams.get('filter');
			return (t === 'all' || t === 'running' || t === 'stopped') ? t : 'all';
		})()
	);

	// ─── Derived ──────────────────────────────────────────────────────────────
	let filtered = $derived(
		filter === 'all'
			? containers
			: filter === 'running'
				? containers.filter((c) => c.status === 'running')
				: containers.filter((c) => c.status !== 'running')
	);

	let grouped = $derived(
		CATEGORY_ORDER.reduce<Record<ContainerCategory, Container[]>>(
			(acc, cat) => {
				const members = filtered.filter((c) => {
					const meta = CONTAINER_META[c.name];
					return meta ? meta.category === cat : cat === 'app'; // uncategorised → app
				});
				if (members.length > 0) acc[cat] = members;
				return acc;
			},
			{} as Record<ContainerCategory, Container[]>
		)
	);

	let runningCount = $derived(containers.filter((c) => c.status === 'running').length);
	let stoppedCount = $derived(containers.filter((c) => c.status !== 'running').length);

	// ─── Load ─────────────────────────────────────────────────────────────────

	async function loadContainers() {
		loading = true;
		error = '';
		try {
			containers = await fetchContainers();
		} catch (e) {
			error = 'Could not load containers. ';
			console.error(e);
		} finally {
			loading = false;
		}
	}
	onMount(async () => {
		loadContainers();
	});

	const sectionClass =
		'font-mono text-xs font-bold tracking-widest uppercase text-gray-500 flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10 mb-4';
</script>

<InteractionBar tabs={filters} tab={filter} loadData={loadContainers} paramKey="filter" />
{#if !loading}
	<p class="font-mono text-xs text-gray-500 mt-2 mb-4">
		<span class="text-green-400">{runningCount} running</span>
		{#if stoppedCount > 0}
			&nbsp;·&nbsp;<span class="text-red-400">{stoppedCount} stopped</span>
		{/if}
	</p>
{/if}

{#if loading}
	<!-- Skeleton -->
	<div class="space-y-8">
		{#each Array(3) as _, i (i)}
			<div>
				<div class="h-4 w-24 rounded bg-white/5 mb-4 animate-pulse"></div>
				<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
					{#each Array(4) as _, j (j)}
						<div class="h-28 rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
					{/each}
				</div>
			</div>
		{/each}
	</div>
{:else if error}
	<p class="font-mono text-xs text-red-400">{error}</p>
{:else}
	<div class="space-y-8">
		{#each Object.entries(grouped) as [cat, members], i (i)}
			<section>
				<h2 class={sectionClass}>
					{CATEGORY_LABELS[cat as ContainerCategory]}
					<span class="text-gray-600 font-normal normal-case tracking-normal">{members.length}</span>
				</h2>
				<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
					{#each members as container (container.name)}
						<ContainerCard {container} />
					{/each}
				</div>
			</section>
		{/each}

		{#if Object.keys(grouped).length === 0}
			<p class="font-mono text-xs text-gray-600">No containers match the current filter.</p>
		{/if}
	</div>
{/if}
