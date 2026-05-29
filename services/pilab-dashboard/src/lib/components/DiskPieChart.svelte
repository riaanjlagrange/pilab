<script lang="ts">
  import { Pie } from 'svelte-chartjs';
  import {
    Chart as ChartJS, Title, Tooltip,
    Legend, ArcElement, CategoryScale,
  } from 'chart.js';
  import ChartDataLabels from 'chartjs-plugin-datalabels';
  import { fetchDisk } from '$lib/api';
  import InternalButton from '$lib/components/InternalButton.svelte';
	import { onMount } from 'svelte';

  ChartJS.register(Title, Legend, ArcElement, CategoryScale, ChartDataLabels);

  let { height = 90, compact = false } = $props();

  let diskUsed = $state(0);
  let diskFree = $state(0);
  let diskTotal = $state(0);
  let diskPct = $state(0);

  async function loadDisk() {
    const res = await fetchDisk();
    diskUsed = res.used_gb;
    diskFree = res.free_gb;
    diskTotal = res.total_gb;
    diskPct = res.percent_used;
  }

  onMount(() => {
    loadDisk();
  });

  const chartData = $derived({
    labels: ['Used', 'Free'],
    datasets: [{
      data: [diskUsed, diskFree],
      backgroundColor: ['#ef4444', '#22c55e'],
      borderColor: ['#dc2626', '#16a34a'],
      borderWidth: 0.1,
    }],
  });

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
      datalabels: { display: false },
    },
  };
</script>

{#if compact}
  <!-- Navbar variant -->
  <div class="flex items-center gap-3 rounded-xl px-2 py-1">
    <div style="width: {height}px; height: {height}px; flex-shrink: 0;">
      <Pie data={chartData} options={chartOptions} />
    </div>
    <div class="min-w-0">
      <div class="mb-0.5 flex items-center gap-1.5">
        <!-- heroicon or lucide -->
        <i class="ti ti-hard-drive text-sm text-red-500"></i>
      </div>
      <div class="text-xs font-medium">
        {diskPct}%
      </div>
    </div>
  </div>

{:else}
  <!-- Dashboard card variant -->
  <div class="rounded-md bg-zinc-800 p-4 w-full h-full">
    <div class="mb-4 flex items-center justify-between">
      <span class="text-sm font-medium">Disk usage</span>
    </div>

    <div class="flex items-center gap-5">
      <div class="w-full flex items-center justify-center">
        <div style="height: {height}px; width: {height}px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
          <Pie data={chartData} options={chartOptions} />
        </div>
      </div>
      <div class="flex flex-col gap-3 min-w-20">
        <div>
          <div class="mb-0.5 flex items-center gap-1.5">
            <span class="inline-block h-2 w-2 rounded-sm bg-red-500"></span>
            <span class="text-xs">Used</span>
          </div>
          <span class="font-mono text-sm font-medium">{diskUsed} <span class="text-xs font-mono text-gray-500">GB</span></span>
        </div>
        <div>
          <div class="mb-0.5 flex items-center gap-1.5">
            <span class="inline-block h-2 w-2 rounded-sm bg-green-500"></span>
            <span class="text-xs text-muted-foreground">Free</span>
          </div>
          <span class="font-mono text-sm font-medium">{diskFree} <span class="text-xs font-mono text-gray-500">GB</span></span>
        </div>
      </div>
    </div>
    <div class="mt-5">
      <InternalButton icon="folder" label="Manage disk" href="/manager?tab=library" />
    </div>
  </div>
{/if}