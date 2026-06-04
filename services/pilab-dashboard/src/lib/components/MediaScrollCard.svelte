<script lang="ts">
  import type { CardMedia, SearchResult } from '$lib/types.d.ts';

  let {
    item,
    onselect,
  }: {
    item:      CardMedia;
    onselect?: (meta: SearchResult) => void;
  } = $props();

  const icon = $derived({
    movie:   'ti-movie',
    series:  'ti-device-tv',
    episode: 'ti-device-tv',
    show:    'ti-device-tv',
  }[item.type] ?? 'ti-photo');

  function handleClick(e: MouseEvent) {
    // If we have a plex link, let the <a> do its thing.
    // If we have meta, open the modal instead.
    if (!item.href && item.meta && onselect) {
      e.preventDefault();
      onselect(item.meta);
    }
  }
</script>

<svelte:element
  this={item.href ? 'a' : 'div'}
  href={item.href ?? undefined}
  target={item.href ? '_blank' : undefined}
  rel={item.href ? 'noopener noreferrer' : undefined}
  role={!item.href ? 'button' : undefined}
  tabindex={!item.href ? 0 : undefined}
  onclick={handleClick}
  onkeydown={(e: KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && !item.href && item.meta && onselect) {
      e.preventDefault();
      onselect(item.meta);
    }
  }}
  class="relative block rounded-lg overflow-hidden aspect-[2/3]
         bg-white/5 border border-white/10 cursor-pointer group select-none"
>
  <!-- Poster -->
  <div class="w-full h-full">
    {#if item.poster_url}
      <img
        src={item.poster_url}
        alt={item.title}
        class="w-full h-full object-cover block transition-transform
               duration-500 group-hover:scale-105"
        loading="lazy"
      />
    {:else}
      <div class="w-full h-full flex flex-col items-center justify-center gap-2 bg-white/[0.03]">
        <i class="ti {icon} text-white/15 text-3xl"></i>
        <p class="font-mono text-[0.6rem] text-white/20 text-center px-2 leading-tight line-clamp-3">
          {item.title}
        </p>
      </div>
    {/if}
  </div>

  <!-- Badge -->
  {#if item.badge}
    <div class="absolute top-2 right-2 z-10">
      <span class="font-mono text-[0.55rem] font-bold tracking-wider uppercase px-1.5 py-0.5 rounded
        {item.owned
          ? 'bg-[#e5a00d]/90 text-black'
          : 'bg-white/10 text-white/70 border border-white/20'}">
        {item.badge}
      </span>
    </div>
  {/if}

  <!-- Hover overlay -->
  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200
              bg-gradient-to-t from-black/95 via-black/50 to-transparent
              flex items-end pointer-events-none">
    <div class="p-3 w-full">

      {#if item.href}
        <i class="ti ti-player-play-filled text-[#e5a00d] text-base mb-1.5 block"></i>
      {:else if item.meta}
        <i class="ti ti-info-circle text-white/60 text-base mb-1.5 block"></i>
      {:else}
        <i class="ti {icon} text-white/40 text-base mb-1.5 block"></i>
      {/if}

      <p class="font-mono text-[0.7rem] font-bold text-white leading-tight line-clamp-2">
        {item.title}
      </p>

      {#if item.year}
        <p class="font-mono text-[0.6rem] text-white/40 mt-0.5">{item.year}</p>
      {/if}

      {#if item.subtitle}
        <p class="font-mono text-[0.62rem] text-white/60 truncate mt-0.5">{item.subtitle}</p>
      {/if}

      {#if item.progress_pct}
        <div class="mt-2 h-0.5 w-full bg-white/15 rounded-full overflow-hidden">
          <div
            class="h-full bg-[#e5a00d] rounded-full"
            style="width: {item.progress_pct}%"
          ></div>
        </div>
      {/if}

    </div>
  </div>
</svelte:element>