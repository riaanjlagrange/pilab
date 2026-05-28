<script lang="ts">
	let { title, subtitle = '' }: { title: string; subtitle?: string } = $props();
</script>

<div class="mb-6">
	<h1 class="font-mono text-lg font-bold tracking-wide text-gray-200">{title}</h1>
	{#if subtitle}
		<p class="mt-1 font-mono text-xs text-gray-500">{subtitle}</p>
	{/if}
</div>
