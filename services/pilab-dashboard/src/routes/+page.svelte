<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchSystem, fetchDisk, fetchPlex, fetchSettings } from '$lib/api';
	import type { SystemStats, DiskStats, PlexData, Alert } from '$lib/types.d.ts';
	import SysBar from '$lib/components/SysBar.svelte';
	import SysChip from '$lib/components/SysChip.svelte';
	import AlertBanner from '$lib/components/AlertBanner.svelte';
	import NowPlaying from '$lib/components/NowPlaying.svelte';
	import OnDeckCard from '$lib/components/OnDeckCard.svelte';

	// ─── State ────────────────────────────────────────────────────────────────
	let system = $state<SystemStats | null>(null);
	let disk = $state<DiskStats | null>(null);
	let plex = $state<PlexData | null>(null);
	let diskThreshold = $state(85);
	let pilabName = $state('');
	let loading = $state(true);
	let errors = $state<string[]>([]);

	// ─── Derived ──────────────────────────────────────────────────────────────
	let diskUsed = $derived(disk ? disk.percent_used : 0);

	let alerts = $derived<Alert[]>([
		...(disk && diskUsed >= diskThreshold
			? [
					{
						id: 'disk-threshold',
						type: 'warning' as const,
						message: `Disk usage is at ${diskUsed}% — above your ${diskThreshold}% threshold. Free: ${disk.free_gb.toFixed(1)} GB.`,
						link: `/media?tab=media`,
						linkLabel: 'Media Manager'
					}
				]
			: []),
		...errors.map((e, i) => ({
			id: `err-${i}`,
			type: 'error' as const,
			message: e
		}))
	]);

	// ─── Load ─────────────────────────────────────────────────────────────────
	onMount(async () => {
		const results = await Promise.allSettled([
			fetchSystem(),
			fetchDisk(),
			fetchPlex(),
			fetchSettings()
		]);

		if (results[0].status === 'fulfilled') system = results[0].value;
		else errors = [...errors, `System stats unavailable`];

		if (results[1].status === 'fulfilled') disk = results[1].value;
		else errors = [...errors, `Disk stats unavailable`];

		if (results[2].status === 'fulfilled') plex = results[2].value;
		// plex silently fails — no active streams is normal

		if (results[3].status === 'fulfilled') {
			diskThreshold = results[3].value.diskThreshold;
			pilabName = results[3].value.pilabName;
		}

		loading = false;
	});

	// ─── Section header helper ────────────────────────────────────────────────
	const sectionClass =
		'font-mono text-xs font-bold tracking-widest uppercase text-gray-500 flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10 mb-4';
</script>

<!-- Alerts -->
<AlertBanner {alerts} />

<!-- System stats -->
<section class="mb-8">
	<h2 class={sectionClass}>
		<i class="ti ti-cpu text-xs"></i>
		System
	</h2>

	{#if loading}
		<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
			{#each Array(4) as _, i (i)}
				<div id={_} class="h-16 rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
			{/each}
		</div>
	{:else if system}
		<div class="rounded-lg bg-white/5 border border-white/10 p-4 space-y-4">
			<!-- Chips row -->
			<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
				<SysChip label="Name" value={pilabName} icon="ti-server" />
				{#if disk}
					<SysChip label="Used" value="{diskUsed}%" icon="ti-chart-pie" />
					<SysChip label="Free" value="{disk.free_gb.toFixed(1)} GB" icon="ti-database" />
				{/if}
			</div>

			<!-- Bars -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
				<SysBar label="CPU" value={system.cpu_percent} icon="ti-cpu" />
				<SysBar label="RAM" value={system.ram_percent} icon="ti-circuit-board" />
				{#if disk}
					<SysBar
						label="Disk"
						value={diskUsed}
						icon="ti-database"
						warnAt={disk.percent_used - 10}
						dangerAt={disk.percent_used}
					/>
				{/if}
			</div>
		</div>
	{:else}
		<p class="font-mono text-xs text-gray-600">Could not load system stats.</p>
	{/if}
</section>

<!-- Plex -->
<section class="mb-8">
	<h2 class={sectionClass}>
		<i class="ti ti-movie -xs"></i>
		Plex
	</h2>

	{#if loading}
		<div class="h-24 rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
	{:else if plex}
		<!-- Now playing -->
		{#if plex.now_playing.length > 0}
			<div class="mb-4 space-y-3">
				<p class="font-mono text-xs text-gray-500 uppercase tracking-widest">Now Playing</p>
				{#each plex.now_playing as item, i (i)}
					<NowPlaying {item} />
				{/each}
			</div>
		{:else}
			<p class="font-mono text-xs text-gray-600 mb-4">Nothing streaming right now.</p>
		{/if}

		<!-- On Deck -->
		{#if plex.on_deck.length > 0}
			<div>
				<p class="font-mono text-xs text-gray-500 uppercase tracking-widest mb-3">On Deck</p>
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
					{#each plex.on_deck.slice(0, 6) as item, i (i)}
						<OnDeckCard {item} />
					{/each}
				</div>
			</div>
		{/if}
	{:else}
		<p class="font-mono text-xs text-gray-600">Plex unavailable.</p>
	{/if}
</section>
