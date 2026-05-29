<script lang="ts" generics="T extends string">
	type Props = {
		items: T[] | { value: T; label?: string }[];
		active: T;
		size?: 'sm' | 'md';
		// Link mode
		href?: (value: T) => string;
		reload?: boolean;
		// Button mode
		onchange?: (value: T) => void;
	};

	let {
		items,
		active,
		size = 'md',
		href,
		reload = false,
		onchange
	}: Props = $props();

	function normalize(item: T | { value: T; label?: string }): { value: T; label: string } {
		if (typeof item === 'string') {
			return { value: item, label: item.charAt(0).toUpperCase() + item.slice(1) };
		}
		return { value: item.value, label: item.label ?? (item.value.charAt(0).toUpperCase() + item.value.slice(1)) };
	}

	const normalized = $derived(items.map(normalize));

	const padding = $derived(size === 'sm' ? 'px-3 py-1.5' : 'px-4 py-2');
</script>

<div class="flex items-center gap-1 rounded-md bg-white/5 border border-white/10 p-1 w-fit">
	{#each normalized as item (item.value)}
		{#if href}
			<a
				href={href(item.value)}
				data-sveltekit-reload={reload ? true : undefined}
				class="font-mono cursor-pointer text-xs {padding} rounded transition-all capitalize
				       {active === item.value ? 'bg-white/10 text-gray-200' : 'text-gray-500 hover:text-gray-300'}"
			>
				{item.label}
			</a>
		{:else}
			<button
				onclick={() => onchange?.(item.value)}
				class="font-mono cursor-pointer text-xs {padding} rounded transition-all duration-150
				       {active === item.value ? 'bg-white/10 text-gray-200' : 'text-gray-500 hover:text-gray-300'}"
			>
				{item.label}
			</button>
		{/if}
	{/each}
</div>