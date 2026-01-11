<script>
  export let wordDefinitionData = [];
</script>

<div class="flex flex-col items-center justify-center h-full p-6 space-y-6">
  {#each wordDefinitionData as word}
    <div class="text-center">
      {#if word.language}
        <p class="text-xs text-base-content/60 uppercase tracking-wider mb-1">{word.language}</p>
      {/if}
      <p class="text-2xl md:text-3xl font-bold text-base-content">{word.original}</p>
      {#if word.transliteration}
        <p class="text-lg text-base-content/70 italic">{word.transliteration}</p>
      {/if}
      {#if word.definition}
        <p class="text-base text-base-content/80 mt-2 max-w-md">{word.definition}</p>
      {/if}
    </div>
  {/each}
</div>
