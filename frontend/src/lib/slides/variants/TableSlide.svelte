<script>
  export let body = '';
  export let title = '';
</script>

<div class="flex flex-col h-full p-6 overflow-auto">
  {#if title}
    <h2 class="text-xl font-bold text-base-content mb-4">{title}</h2>
  {/if}
  <div class="prose prose-sm max-w-none">
    {@html body}
  </div>
</div>
