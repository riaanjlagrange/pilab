<script lang="ts">
	let {
		label,
		value,
		unit = '',
		icon = ''
	}: {
		label: string;
		value: string | number;
		unit?: string;
		icon?: string;
	} = $props();
</script>

<div class="flex flex-col items-center justify-center gap-2 w-full h-full bg-white/5 rounded-sm border border-white/10 px-3 py-2">
	{#if icon}
		<i class="ti {icon} text-gray-500 text-sm"></i>
	{/if}
	<span class="font-mono text-xs text-gray-500 uppercase tracking-widest">{label}</span>
	<span class="font-mono text-sm font-bold text-gray-200">{value}{unit}</span>
</div>
