<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchSystem, fetchDisk, fetchSettings } from '$lib/api';
  import type { SystemStats, DiskStats, Alert } from '$lib/types.d.ts';
  import SysChip     from '$lib/components/SysChip.svelte';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import DiskPieChart from '$lib/components/DiskPieChart.svelte';

  // ─── State ────────────────────────────────────────────────────────────────
  let system        = $state<SystemStats | null>(null);
  let disk          = $state<DiskStats | null>(null);
  let diskThreshold = $state(85);
  let loading       = $state(true);
  let errors        = $state<string[]>([]);

  // ─── Derived ──────────────────────────────────────────────────────────────
  let diskUsed = $derived(disk ? disk.percent_used : 0);
  let diskFree = $derived(disk ? disk.free_gb : 0);

  let alerts = $derived<Alert[]>([
    ...(disk && diskUsed >= diskThreshold
      ? [{
          id:        'disk-threshold',
          type:      'warning' as const,
          message:   `Disk usage is at ${diskUsed}% — above your ${diskThreshold}% threshold. Free: ${diskFree.toFixed(1)} GB.`,
          link:      '/manager?tab=library',
          linkLabel: 'Media Manager',
        }]
      : []),
    ...errors.map((e, i) => ({
      id:      `err-${i}`,
      type:    'error' as const,
      message: e,
    })),
  ]);

  // ─── Load ─────────────────────────────────────────────────────────────────
  async function loadStats(isBackground = false) {
    if (!isBackground) loading = true;
    errors = [];
    const [systemRes, diskRes] = await Promise.allSettled([
      fetchSystem(),
      fetchDisk(),
    ]);
    if (systemRes.status === 'fulfilled') system = systemRes.value;
    else errors = [...errors, 'Failed to load system stats.'];
    if (diskRes.status === 'fulfilled') disk = diskRes.value;
    if (!isBackground) loading = false;
  }

  async function loadSettings() {
    try {
      const res = await fetchSettings();
      diskThreshold = res.diskThreshold;
    } catch (e) {
      console.error('Failed to load settings', e);
      errors = [...errors, 'Failed to load settings.'];
    }
  }

  onMount(() => {
    loadSettings();
    loadStats().then(() => { loading = false; });
    const interval = setInterval(() => loadStats(true), 2000);
    return () => clearInterval(interval);
  });
</script>

<AlertBanner {alerts} />

<section class="mb-8">
  {#if loading}
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      {#each Array(4) as _, i (i)}
        <div class="h-16 rounded-lg bg-white/5 border border-white/10 animate-pulse"></div>
      {/each}
    </div>
  {:else if system}
    <p class="font-mono text-xs text-gray-500 uppercase tracking-widest mb-3">System</p>
    <div class="flex flex-col gap-3 sm:flex-row rounded-lg">
      <DiskPieChart height={180} />
      <div class="grid grid-cols-2 gap-3 w-full">
        <SysChip label="Uptime"   value={system.uptime_human}        icon="ti-clock"       />
        <SysChip label="RAM"      value={system.ram_percent + '%'}   icon="ti-cpu"         />
        <SysChip label="CPU"      value={system.cpu_percent + '%'}   icon="ti-cpu"         />
        <SysChip label="CPU Temp" value={system.cpu_temp + '°C'}     icon="ti-thermometer" />
      </div>
    </div>
  {:else}
    <p class="font-mono text-xs text-gray-600">Could not load system stats.</p>
  {/if}
</section>