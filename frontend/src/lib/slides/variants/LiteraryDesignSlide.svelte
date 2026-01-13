<script>
  export let title = '';
  export let html = '';
  export let reference = '';
</script>

<div class="flex flex-col h-full p-6">
  {#if title}
    <h2 class="text-xl font-bold mb-2 text-center">{title}</h2>
  {/if}
  {#if reference}
    <p class="text-sm text-base-content/70 mb-4 text-center">{reference}</p>
  {/if}
  <div class="flex-1 overflow-y-auto prose prose-sm max-w-none">
    {#if html}
      {@html html}
    {:else}
      <p class="text-base-content/60 text-center">Literary design content</p>
    {/if}
  </div>
</div>
