<script lang="ts">
  import { page } from '$app/stores';

  let { open = $bindable(false) }: { open: boolean } = $props();

  const links = [
    { href: '/',          label: 'Home',      icon: 'ti-home'        },
    { href: '/library',   label: 'Library',   icon: 'ti-database'    },
    { href: '/downloads', label: 'Downloads', icon: 'ti-download'    },
    { href: '/services',  label: 'Services',  icon: 'ti-layout-grid' },
    { href: '/system',  label: 'System',  icon: 'ti-server' },
    { href: '/settings',  label: 'Settings',  icon: 'ti-settings'    },
  ];

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false;
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <!-- Backdrop -->
  <div
    class="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
    role="button"
    tabindex="-1"
    aria-label="Close menu"
    onclick={() => (open = false)}
    onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') open = false; }}
  ></div>

  <!-- Drawer -->
  <div
    class="fixed left-0 top-12 z-50 h-[calc(100vh-3rem)] w-56
           bg-[#0a0a0a] border-r border-white/10
           flex flex-col overflow-y-auto"
    role="navigation"
    aria-label="Main menu"
  >
    <nav class="flex-1 px-2 py-3 space-y-0.5">
      {#each links as link}
        {@const active = $page.url.pathname === link.href}
        <a
          href={link.href}
          onclick={() => (open = false)}
          class="flex items-center gap-3 px-3 py-2.5 rounded-md transition-all duration-150
                 {active
                   ? 'bg-white/8 text-white border border-white/15'
                   : 'text-gray-500 hover:text-gray-200 hover:bg-white/5 border border-transparent'}"
        >
          <i class="ti {link.icon} text-sm shrink-0
                    {active ? 'text-[#e5a00d]' : ''}"></i>
          <span class="font-mono text-xs">{link.label}</span>
        </a>
      {/each}
    </nav>
  </div>
{/if}