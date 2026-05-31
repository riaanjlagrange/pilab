<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchDownloads } from '$lib/api';
	import type { Download } from '$lib/types.d.ts';

	// ─── State ────────────────────────────────────────────────────────────────
	let downloads = $state<Download[]>([]);

	// ─── Derived ──────────────────────────────────────────────────────────────

	// Only items that are actively pulling bytes
	let active = $derived(
		downloads.filter((d) => d.status === 'downloading' || d.status === 'forcedDL')
	);

	// Sum of speed across all active items (MB/s)
	let totalSpeed = $derived(
		active.reduce((sum, d) => sum + (d.speed_mb ?? 0), 0)
	);

	// Weighted average progress across active items
	let avgProgress = $derived(
		active.length
			? active.reduce((sum, d) => sum + (d.progress ?? 0), 0) / active.length
			: 0
	);

	// ─── Poll ─────────────────────────────────────────────────────────────────
	async function poll() {
		try {
			downloads = await fetchDownloads();
		} catch {
			// silently fail — this is ambient UI, not critical
		}
	}

	onMount(() => {
		poll();
		const interval = setInterval(poll, 3000);
		return () => clearInterval(interval);
	});

	// ─── Helpers ──────────────────────────────────────────────────────────────
	function fmtSpeed(mbs: number): string {
		if (mbs >= 1) return `${mbs.toFixed(1)} MB/s`;
		return `${(mbs * 1024).toFixed(0)} KB/s`;
	}
</script>

{#if active.length > 0}
	<a
		href="/manager?tab=queue"
		title="{active.length} active download{active.length > 1 ? 's' : ''}"
		class="group relative flex items-center gap-1.5 rounded-md border border-blue-500/20 bg-blue-500/10
		       px-2.5 py-1.5 transition-all hover:border-blue-500/40 hover:bg-blue-500/20"
	>

		<!-- Animated download icon -->
		<i class="ti ti-download text-xs text-blue-400 transition-transform group-hover:-translate-y-px"></i>

		<!-- Speed -->
		<span class="font-mono text-[10px] leading-none text-blue-300/80">
			{fmtSpeed(totalSpeed)}
		</span>

		<!-- Count badge — only if > 1 -->
		{#if active.length > 1}
			<span
				class="flex h-3.5 w-3.5 items-center justify-center rounded-full bg-blue-500/30
				       font-mono text-[9px] leading-none text-blue-300"
			>
				{active.length}
			</span>
		{/if}
	</a>
{/if}