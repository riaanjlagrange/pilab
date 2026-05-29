<script lang="ts">
  import { goto } from '$app/navigation';

  let { icon, label, href } = $props();
</script>

<button
  onclick={() => goto(href)}
  class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-md bg-background hover:bg-zinc-900 px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
>
  <i class="ti ti-{icon}" aria-hidden="true"></i>
  {label}
</button>