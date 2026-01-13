<script>
  export let title = '';
  export let multiVerseData = [];
</script>

<div class="flex flex-col h-full p-6">
  {#if title}
    <h2 class="text-xl font-bold mb-4 text-center">{title}</h2>
  {/if}
  <div class="flex-1 overflow-y-auto space-y-4">
    {#each multiVerseData as verse}
      <div class="p-4 bg-base-300/50 rounded-lg">
        <p class="text-lg leading-relaxed">{verse.text || ''}</p>
        {#if verse.reference}
          <cite class="block mt-2 text-sm text-base-content/70 not-italic font-semibold">
            {verse.reference}
          </cite>
        {/if}
      </div>
    {/each}
  </div>
</div>
