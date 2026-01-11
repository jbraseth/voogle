<script>
  export let resolved_assets = {};
  export let caption = '';

  $: diagramSrc = resolved_assets?.diagramArcId || '';
</script>

<div class="flex flex-col items-center justify-center h-full p-6">
  {#if diagramSrc}
    <img src={diagramSrc} alt={caption || 'Diagram'} class="max-w-full max-h-[70%] object-contain" />
  {/if}
  {#if caption}
    <p class="text-sm text-base-content/70 mt-4 text-center">{caption}</p>
  {/if}
</div>
