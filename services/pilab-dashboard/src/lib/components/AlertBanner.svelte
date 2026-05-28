<script lang="ts">
	import type { Alert } from '$lib/types';

	let { alerts = [] }: { alerts: Alert[] } = $props();

	let dismissed = $state<Set<string>>(new Set());
	let visible = $derived(alerts.filter((a) => !dismissed.has(a.id)));

	function dismiss(id: string) {
		dismissed = new Set([...dismissed, id]);
	}

	const styles: Record<string, string> = {
		error: 'border-red-500/30 bg-red-500/10 text-red-400',
		warning: 'border-yellow-500/30 bg-yellow-500/10 text-yellow-400',
		info: 'border-blue-500/30 bg-blue-500/10 text-blue-400'
	};
</script>

{#if visible.length > 0}
	<div class="space-y-2 mb-4">
		{#each visible as alert (alert.id)}
			<div class="flex items-center gap-3 rounded-md border px-4 py-3 {styles[alert.type]}">
				<i class="ti ti-database text-base shrink-0"></i>
				<span class="font-mono text-xs flex-1">{alert.message}</span>
				{#if alert.link}
					<a
						href={alert.link}
						class="shrink-0 px-3 py-1 rounded text-xs font-mono bg-current/20 hover:bg-current/30 transition-colors"
					>
						{alert.linkLabel || 'View'}
					</a>
				{/if}
				<button
					onclick={() => dismiss(alert.id)}
					class="shrink-0 opacity-50 hover:opacity-100 transition-opacity"
					aria-label="Dismiss"
				>
					<i class="ti ti-x text-sm"></i>
				</button>
			</div>
		{/each}
	</div>
{/if}
