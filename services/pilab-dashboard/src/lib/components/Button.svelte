<script lang="ts">
  import { goto } from '$app/navigation';
  let { icon, label, href, external = false } = $props();
</script>

{#if external}
  <a
    {href}
    target="_blank"
    rel="noopener noreferrer"
    class="flex cursor-pointer shrink-0 items-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-gray-300 transition-all hover:bg-white/10 disabled:opacity-50"
  >
    <i class="ti ti-{icon}" aria-hidden="true"></i>
    {label}
  </a>
{:else}
  <button
    onclick={() => goto(href)}
    class="flex cursor-pointer shrink-0 items-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-gray-300 transition-all hover:bg-white/10 disabled:opacity-50"
  >
    <i class="ti ti-{icon}" aria-hidden="true"></i>
    {label}
  </button>
{/if}