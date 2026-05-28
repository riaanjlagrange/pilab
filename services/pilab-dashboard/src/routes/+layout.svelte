<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { fetchSystem } from '$lib/api';
	import { env } from '$env/dynamic/public';
	import './layout.css';

	let { children } = $props();
	let pilabName = $state('');

	const NAV = [
		{ href: '/', label: 'Home', icon: 'ti-home' },
		{ href: '/services', label: 'Services', icon: 'ti-brand-docker' },
		{ href: '/media', label: 'Media Manager', icon: 'ti-database' },
		{ href: '/settings', label: 'Settings', icon: 'ti-settings' }
	];

	let currentPath = $derived($page.url.pathname);

	function isActive(href: string): boolean {
		if (href === '/') return currentPath === '/';
		return currentPath.startsWith(href);
	}

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

<div class="min-h-screen bg-[#0a0c0f] text-gray-200">
	<!-- Nav bar -->
	<nav class="sticky top-0 z-50 border-b border-white/10 bg-[#0a0c0f]/80 backdrop-blur-md">
		<div class="max-w-6xl mx-auto px-4 flex items-center h-12 gap-1">
			<!-- Logo / wordmark -->
			<a href="/" class="font-mono text-sm font-bold text-gray-200 mr-4 flex items-center gap-2">
				<i class="ti ti-circuit-diode text-blue-400"></i>
				{pilabName || 'rpi'}
			</a>

			<!-- Tabs -->
			{#each NAV as item, i (i)}
				<a
					href={item.href}
					class="flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs transition-all duration-150
					       {isActive(item.href)
						       ? 'bg-white/10 text-gray-200'
						       : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'}"
				>
					<i class="ti {item.icon} text-sm"></i>
					{item.label}
				</a>
			{/each}

			<!-- Spacer + hostname badge -->
			<div class="ml-auto font-mono text-xs text-gray-600 flex items-center gap-1.5">
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
