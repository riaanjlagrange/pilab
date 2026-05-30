<script lang="ts">
    import FilterControl from './FilterControl.svelte';
    import { goto } from '$app/navigation';
    import RefreshButton from './RefreshButton.svelte';
    export interface Tab {
        value: string;
        label: string;
    }
    let { tabs, tab, loadData, paramKey }: { tabs: Tab[]; tab: string; loadData: () => void; paramKey: string } = $props();
</script>

<div class="mb-6 flex items-center justify-between gap-4">
    <FilterControl
        items={tabs}
        active={tab}
        size="sm"
        onchange={(t) => {
            goto(`?${paramKey}=${t}`, { replaceState: true });
        }}
    />
    <RefreshButton onclick={loadData} />
</div>