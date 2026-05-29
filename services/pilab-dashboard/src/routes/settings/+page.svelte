<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchSettings, saveSettings, fetchContainers } from '$lib/api';
	import { env } from '$env/dynamic/public';

	// ─── State ────────────────────────────────────────────────────────────────
	let diskThreshold = $state(85);
	let pilabName = $state('');
	let hiddenContainers = $state<string[]>([]);
	let checkIntervalMinutes = $state(60);
	let ntfyTopic = $state('');

	let loading = $state(true);
	let saved = $state(false);
	let error = $state('');
	let saveTimeout: ReturnType<typeof setTimeout>;

	// Container name list for the hidden-containers picker
	let allContainerNames = $state<string[]>([]);

	// ─── Load settings ────────────────────────────────────────────────────────
	onMount(async () => {
		try {
			// Fetch settings
			const settings = await fetchSettings();
			diskThreshold = settings.diskThreshold ?? 85;
			pilabName = settings.pilabName ?? '';
			hiddenContainers = settings.hiddenContainers ?? [];
			checkIntervalMinutes = settings.checkIntervalMinutes ?? 60;
			ntfyTopic = settings.ntfyTopic ?? '';

			// Fetch all containers from API
			const containers = await fetchContainers(true);
			allContainerNames = containers.map((c) => c.name).sort();
		} catch (e) {
			error = 'Failed to load settings';
			console.error(e);
		} finally {
			loading = false;
		}
	});

	async function saveConfig() {
		try {
			await saveSettings({
				diskThreshold,
				pilabName,
				hiddenContainers,
				checkIntervalMinutes,
				ntfyTopic
			});
			saved = true;
			clearTimeout(saveTimeout);
			saveTimeout = setTimeout(() => (saved = false), 2500);
		} catch (e) {
			error = 'Failed to save settings';
			console.error(e);
		}
	}

	function resetConfig() {
		diskThreshold = 85;
		pilabName = '';
		hiddenContainers = [];
		checkIntervalMinutes = 60;
		ntfyTopic = '';
		saveConfig();
	}

	function toggleHidden(name: string) {
		if (hiddenContainers.includes(name)) {
			hiddenContainers = hiddenContainers.filter((n) => n !== name);
		} else {
			hiddenContainers = [...hiddenContainers, name];
		}
	}

	// ─── Helpers ──────────────────────────────────────────────────────────────
	const sectionClass =
		'font-mono text-xs font-bold tracking-widest uppercase text-gray-500 flex items-center gap-3 after:flex-1 after:h-px after:bg-white/10 mb-4';

	const inputClass =
		'w-full rounded-md bg-white/5 border border-white/10 px-3 py-2 font-mono text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-blue-400/50 focus:bg-white/8 transition-all';

	let thresholdColor = $derived(
		diskThreshold >= 90 ? 'text-red-400' : diskThreshold >= 80 ? 'text-yellow-400' : 'text-green-400'
	);
</script>

<div class="max-w-2xl">
	<!-- ─── Header ─────────────────────────────────────────────────────────── -->
	<div class="mb-8">
		<h1 class="font-mono text-lg font-bold tracking-wide text-gray-200">Settings</h1>
		<p class="font-mono text-xs text-gray-500 mt-1">
			Manage your homelab configuration, including alert thresholds, hostnames, and hidden containers.
		</p>
	</div>

	{#if error}
		<div class="mb-4 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-3">
			<i class="ti ti-alert-circle text-red-400 text-sm"></i>
			<span class="font-mono text-xs text-red-400">{error}</span>
		</div>
	{/if}

	{#if loading}
		<div class="space-y-4">
			{#each Array(3) as _, i (i)}
				<div id={_} class="h-20 rounded-lg bg-white/5 animate-pulse"></div>
			{/each}
		</div>
	{:else}
		<!-- ─── General ──────────────────────────────────────────────────────────── -->
		<section class="mb-8">
			<h2 class={sectionClass}>
				<i class="ti ti-adjustments text-xs"></i>
				General
			</h2>

			<div class="rounded-lg bg-white/5 border border-white/10 divide-y divide-white/5">
				<!-- Host -->
				<div class="p-4 space-y-2">
					<label class="font-mono text-xs text-gray-400 uppercase tracking-widest" for="host">
						Pilab Name
					</label>
					<input
						id="host"
						type="text"
						bind:value={pilabName}
						placeholder="e.g. rpi, pilab, homelab"
						class={inputClass}
					/>
					<p class="font-mono text-xs text-gray-600">
						The name of your pilab instance.
					</p>
				</div>

				<!-- Check interval -->
				<div class="p-4 space-y-2">
					<div class="flex items-center justify-between">
						<label class="font-mono text-xs text-gray-400 uppercase tracking-widest" for="check-interval">
							Monitor interval
						</label>
						<span class="font-mono text-sm font-bold text-blue-400">{checkIntervalMinutes}m</span>
					</div>
					<input
						id="check-interval"
						type="range"
						min="5"
						max="120"
						step="5"
						bind:value={checkIntervalMinutes}
						class="w-full accent-blue-400 cursor-pointer"
					/>
					<div class="flex justify-between font-mono text-xs text-gray-600">
						<span>5m</span>
						<span>120m</span>
					</div>
					<p class="font-mono text-xs text-gray-600">
						How often the server checks disk space and sends alerts.
					</p>
				</div>

				<!-- Ntfy topic -->
				<div class="p-4 space-y-2">
					<label class="font-mono text-xs text-gray-400 uppercase tracking-widest" for="ntfy-topic">
						Ntfy Topic
					</label>
					<input
						id="ntfy-topic"
						type="text"
						bind:value={ntfyTopic}
						placeholder="my-topic (leave blank to disable)"
						class={inputClass}
					/>
					<p class="font-mono text-xs text-gray-600">
						ntfy.sh topic for disk space alerts. Leave blank to disable notifications.
					</p>
				</div>
			</div>
		</section>

		<!-- ─── Disk ─────────────────────────────────────────────────────────────── -->
		<section class="mb-8">
			<h2 class={sectionClass}>
				<i class="ti ti-database text-xs"></i>
				Disk
			</h2>

			<div class="rounded-lg bg-white/5 border border-white/10 divide-y divide-white/5">
				<!-- Alert threshold -->
				<div class="p-4 space-y-3">
					<div class="flex items-center justify-between">
						<label class="font-mono text-xs text-gray-400 uppercase tracking-widest" for="threshold">
							Alert threshold (%)
						</label>
						<span class="font-mono text-sm font-bold {thresholdColor}">{diskThreshold}%</span>
					</div>
					<input
						id="threshold"
						type="range"
						min="50"
						max="99"
						step="1"
						bind:value={diskThreshold}
						class="w-full accent-blue-400 cursor-pointer"
					/>
					<div class="flex justify-between font-mono text-xs text-gray-600">
						<span>50%</span>
						<span>99%</span>
					</div>
					<p class="font-mono text-xs text-gray-600">
						Alert banner and disk bar turn red when usage exceeds this value.
					</p>
				</div>
			</div>
		</section>

		<!-- ─── Hidden containers ─────────────────────────────────────────────── -->
		<section class="mb-8">
			<h2 class={sectionClass}>
				<i class="ti ti-eye-off text-xs"></i>
				Hidden containers
			</h2>

			<div class="rounded-lg bg-white/5 border border-white/10 p-4">
				<p class="font-mono text-xs text-gray-500 mb-4">
					Checked containers are hidden from the Containers page.
				</p>

				<div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
					{#each allContainerNames as name, i (i)}
						{@const hidden = hiddenContainers.includes(name)}
						<button
							onclick={() => toggleHidden(name)}
							class="flex items-center gap-2 rounded-md px-3 py-2 text-left transition-all
							       border {hidden
								       ? 'border-red-500/30 bg-red-500/10'
								       : 'border-white/10 bg-white/5 hover:bg-white/10'}"
						>
							<i class="ti ti-{hidden ? 'eye-off' : 'eye'} text-xs {hidden ? 'text-red-400' : 'text-gray-500'}"></i>
							<span class="font-mono text-xs {hidden ? 'text-red-400 line-through' : 'text-gray-300'} truncate">
								{name}
							</span>
						</button>
					{/each}
				</div>

				{#if hiddenContainers.length > 0}
					<p class="font-mono text-xs text-gray-500 mt-3">
						{hiddenContainers.length} container{hiddenContainers.length !== 1 ? 's' : ''} hidden.
					</p>
				{/if}
			</div>
		</section>

		<!-- ─── Actions ──────────────────────────────────────────────────────────── -->
		<div class="flex items-center gap-3 flex-wrap">
			<button
				onclick={saveConfig}
				class="flex items-center gap-2 font-mono text-xs px-4 py-2.5 rounded-md
				       bg-blue-500/20 border border-blue-500/30 hover:bg-blue-500/30
				       text-blue-400 transition-all"
			>
				<i class="ti ti-device-floppy text-sm"></i>
				Save settings
			</button>

			<button
				onclick={resetConfig}
				class="flex items-center gap-2 font-mono text-xs px-4 py-2.5 rounded-md
				       bg-white/5 border border-white/10 hover:bg-white/10
				       text-gray-500 hover:text-gray-300 transition-all"
			>
				<i class="ti ti-refresh text-sm"></i>
				Reset to defaults
			</button>

			{#if saved}
				<span class="flex items-center gap-1.5 font-mono text-xs text-green-400">
					<i class="ti ti-check text-sm"></i>
					Saved
				</span>
			{/if}
		</div>

		<!-- ─── Danger zone ───────────────────────────────────────────────────── -->
		<section class="mt-12">
			<h2 class="font-mono text-xs font-bold tracking-widest uppercase text-red-500/50 flex items-center gap-3 after:flex-1 after:h-px after:bg-red-500/20 mb-4">
				<i class="ti ti-alert-triangle text-xs"></i>
				Danger zone
			</h2>

			<div class="rounded-lg border border-red-500/20 bg-red-500/5 p-4 space-y-3">
				<p class="font-mono text-xs text-gray-500">
					These actions affect your running homelab. Use with care.
				</p>

				<div class="flex flex-wrap gap-3">
					<a
						href={`http://${env.PUBLIC_HOST}:9999`}
						target="_blank"
						rel="noopener"
						class="flex items-center gap-2 font-mono text-xs px-3 py-2 rounded-md
						       border border-white/10 bg-white/5 hover:bg-white/10 text-gray-400 transition-all"
					>
						<i class="ti ti-file-description text-sm"></i>
						Container logs
					</a>

					<a
						href={`http://${env.PUBLIC_HOST}:3000`}
						target="_blank"
						rel="noopener"
						class="flex items-center gap-2 font-mono text-xs px-3 py-2 rounded-md
						       border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-red-400/70 transition-all"
					>
						<i class="ti ti-terminal text-sm"></i>
						Terminal
					</a>
				</div>
			</div>
		</section>
	{/if}
</div>
