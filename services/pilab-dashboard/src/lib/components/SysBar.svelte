<script lang="ts">
	import { statusColor, barColor } from '$lib/api';

	let {
		label,
		value,
		unit = '%',
		icon = '',
		warnAt = 70,
		dangerAt = 85
	}: {
		label: string;
		value: number;
		unit?: string;
		icon?: string;
		warnAt?: number;
		dangerAt?: number;
	} = $props();

	let color = $derived(statusColor(value, warnAt, dangerAt));
	let bar = $derived(barColor(value, warnAt, dangerAt));
	let clamped = $derived(Math.min(100, Math.max(0, value)));
</script>

<div class="space-y-1">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			{#if icon}
				<i class="ti {icon} text-gray-500 text-sm"></i>
			{/if}
			<span class="font-mono text-xs text-gray-500 uppercase tracking-widest">{label}</span>
		</div>
		<span class="font-mono text-sm font-bold {color}">{value}{unit}</span>
	</div>
	<div class="h-1 w-full rounded-full bg-white/10 overflow-hidden">
		<div
			class="h-full rounded-full transition-all duration-700 {bar}"
			style="width: {clamped}%"
		></div>
	</div>
</div>
