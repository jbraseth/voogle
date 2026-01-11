<script>
  export let title = '';
  export let content = '';
</script>

<div class="flex flex-col h-full p-8">
  {#if title}
    <h2 class="text-xl md:text-2xl font-bold text-base-content mb-4">{title}</h2>
  {/if}
  <p class="text-base md:text-lg text-base-content/90 leading-relaxed whitespace-pre-wrap">
    {content}
  </p>
</div>
