<script lang="ts">
  import { page } from '$app/stores';

  let { open = $bindable(false) }: { open: boolean } = $props();

  const links = [
    { href: '/',         label: 'Home',         icon: 'ti-home'          },
    { href: '/services', label: 'Services',      icon: 'ti-layout-grid'   },
    { href: '/manager',  label: 'Media Manager', icon: 'ti-device-tv'     },
    { href: '/settings', label: 'Settings',      icon: 'ti-settings'      },
  ];

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false;
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <!-- Backdrop -->
  <div
    class="fixed inset-0 z-40 bg-black/40"
    onclick={() => (open = false)}
  ></div>

  <!-- Drawer -->
  <div
    class="fixed left-0 top-12 z-50 h-screen w-64 bg-black border-r border-white/10 overflow-y-auto flex flex-col transition-transform duration-200"
  >
    <!-- Navigation links -->
    <nav class="flex-1 space-y-1 px-2 py-4">
      {#each links as link}
        {@const active = $page.url.pathname === link.href}
        <a
          href={link.href}
          onclick={() => (open = false)}
          class="cursor-pointer flex items-center gap-3 px-4 py-3 rounded-sm
                 transition-all duration-150
                 {active
                   ? 'bg-white/10 text-white border border-white/20'
                   : 'text-gray-400 hover:text-white hover:bg-white/5'}"
        >
          <i class="ti {link.icon} text-base"></i>
          <span class="font-mono text-sm">{link.label}</span>
        </a>
      {/each}
    </nav>
  </div>
{/if}