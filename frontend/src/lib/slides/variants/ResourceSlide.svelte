<script>
  export let title = '';
  export let authors = [];
</script>

<div class="flex flex-col items-center justify-center h-full p-8">
  <div class="text-center">
    <p class="text-sm uppercase tracking-wider text-base-content/60 mb-2">Recommended Resource</p>
    <h2 class="text-2xl font-bold mb-4">{title}</h2>
    {#if authors && authors.length > 0}
      <p class="text-base text-base-content/70">
        by {authors.join(', ')}
      </p>
    {/if}
  </div>
</div>
