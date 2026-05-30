 <script lang="ts">
    let { onclick } = $props();
    let loading = $state(false);

    async function handleClick() {
        loading = true;
        await onclick();
        loading = false;
    }
 </script>

<button
    onclick={handleClick}
    disabled={loading}
    class="flex cursor-pointer shrink-0 items-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-gray-300 transition-all hover:bg-white/10 disabled:opacity-50"
>
    <i class="ti ti-refresh {loading ? 'animate-spin' : ''} text-sm"></i>
    Refresh
</button>