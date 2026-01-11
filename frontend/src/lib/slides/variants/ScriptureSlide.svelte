<script>
  export let reference = '';
  export let text = '';
  export let verses = [];
</script>

<div class="flex flex-col items-center justify-center h-full p-8">
  {#if reference}
    <p class="text-lg font-semibold text-primary mb-4">{reference}</p>
  {/if}

  {#if text}
    <p class="text-base md:text-lg text-base-content/90 text-center italic leading-relaxed max-w-2xl">
      "{text}"
    </p>
  {/if}

  {#if verses && verses.length > 0}
    <div class="space-y-3 max-w-2xl">
      {#each verses as verse}
        <div class="text-center">
          {#if verse.reference}
            <p class="text-sm font-semibold text-primary mb-1">{verse.reference}</p>
          {/if}
          <p class="text-base md:text-lg text-base-content/90 italic leading-relaxed">
            "{verse.text}"
          </p>
        </div>
      {/each}
    </div>
  {/if}
</div>
