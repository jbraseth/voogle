<script>
  export let resolved_assets = {};
  export let caption = '';

  $: imageSrc = resolved_assets?.imgArcId || '';
</script>

<div class="flex flex-col items-center justify-center h-full p-6">
  {#if imageSrc}
    <img src={imageSrc} alt={caption || 'Image'} class="max-w-full max-h-[70%] object-contain" />
  {/if}
  {#if caption}
    <p class="text-sm text-base-content/70 mt-4 text-center">{caption}</p>
  {/if}
</div>
