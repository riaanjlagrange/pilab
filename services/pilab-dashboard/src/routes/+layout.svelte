<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { fetchSystem } from '$lib/api';
	import { env } from '$env/dynamic/public';
	import './layout.css';
	import DiskPieChart from '$lib/components/DiskPieChart.svelte';
	import DownloadIndicator from '@/components/DownloadIndicator.svelte';
	import NavMenu from '$lib/components/NavMenu.svelte';
	import CommandPalette from '$lib/components/CommandPalette.svelte';

	let paletteOpen = $state(false);
	let navOpen = $state(false);

	let { children } = $props();
	let pilabName = $state('');

	onMount(async () => {
		try {
			const system = await fetchSystem();
			pilabName = system.pilab_name || '';
		} catch (e) {
			console.error('Failed to load host from settings', e);
		}
	});
</script>

<svelte:head>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css" />
</svelte:head>

<CommandPalette bind:open={paletteOpen} />
<NavMenu       bind:open={navOpen} />

<div class="min-h-screen bg-black text-gray-200">
	<!-- Nav bar -->
	<nav class="sticky top-0 z-50 border-b border-white/10 bg-black backdrop-blur-md absolute w-[100vw]">
		<div class="max-w-6xl mx-auto px-4 flex items-center justify-between h-12 gap-5">
			<button
				onclick={() => (navOpen = !navOpen)}
				class="cursor-pointer text-gray-400 hover:text-gray-200 transition-colors p-1 bg-black rounded-sm flex items-center justify-center border border-white/10 hover:border-white/20 transition-colors"
				aria-label="Open menu"
			>
				<i class="ti ti-menu-2 text-xl"></i>
			</button>

			<a href="/" class="font-mono text-sm font-bold text-gray-200 mr-4 flex items-center gap-2">
				<i class="ti ti-circuit-diode text-blue-400"></i>
				{pilabName || 'rpi'}
			</a>

			<button
				onclick={() => (paletteOpen = !paletteOpen)}
				class="cursor-pointer flex-1 max-w-sm mx-auto flex items-center gap-2 px-3 py-1.5 rounded-md bg-white/5 border border-white/10 hover:border-white/20 transition-colors"
			>
				<i class="ti ti-search text-gray-600 text-sm"></i>
				<span class="hidden sm:block font-mono text-xs text-gray-600 flex-1 text-left">
					Search… <span class="text-gray-700">or /radarr /sonarr</span>
				</span>
				<kbd class="hidden sm:block font-mono text-[10px] text-gray-700 border border-white/10 rounded px-1 py-0.5">
					⌘K
				</kbd>
			</button>

			<!-- Spacer + hostname badge -->
			<div class="ml-auto font-mono text-xs text-gray-600 flex items-center gap-1.5">
				<DownloadIndicator />
				<DiskPieChart compact height={20} />
				<i class="ti ti-server text-xs"></i>
				{env.PUBLIC_HOST || 'loading...'}
			</div>
		</div>
	</nav>

	<!-- Page content -->
	<main class="max-w-6xl mx-auto px-4 py-6">
		{@render children()}
	</main>
</div>
