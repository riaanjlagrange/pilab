<script lang="ts">
	import { CONTAINER_META, CONTAINER_URLS } from '$lib/config';
	import type { Container } from '$lib/types';

	let { container }: { container: Container } = $props();

	let meta = $derived(
		CONTAINER_META[container.name] ?? {
			label: container.name,
			icon: 'ti-box',
			category: 'app',
			description: ''
		}
	);

	let url = $derived(CONTAINER_URLS[container.name]);
	let isRunning = $derived(container.status === 'running');

	let statusDot = $derived(
		container.status === 'running'
			? 'bg-green-400'
			: container.status === 'paused'
				? 'bg-yellow-400'
				: container.status === 'restarting'
					? 'bg-blue-400 animate-pulse'
					: 'bg-red-400'
	);
</script>

<a
  href={url && isRunning ? url : undefined}
  target="_blank"
  rel="noopener noreferrer"
  class="group relative flex flex-col gap-3 rounded-lg bg-white/5 border border-white/10
         hover:bg-white/10 hover:border-white/20 transition-all duration-200 p-4
         {url && isRunning ? 'cursor-pointer' : 'cursor-default'}"
>
  <div class="absolute top-3 right-3">
    <span class="inline-block h-2 w-2 rounded-full {statusDot}"></span>
  </div>
  <div class="flex items-start gap-3 pr-4">
    <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-white/5 border border-white/10">
      <i class="ti {meta.icon} text-blue-400 text-lg"></i>
    </div>
    <div class="min-w-0">
      <p class="font-mono text-sm font-bold text-gray-200 truncate">{meta.label}</p>
      {#if meta.description}
        <p class="font-mono text-xs text-gray-500 truncate mt-0.5">{meta.description}</p>
      {/if}
    </div>
  </div>
  <p class="font-mono text-xs text-gray-500 truncate">{container.uptime_human}</p>
</a>
