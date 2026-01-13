<script>
  export let resolved_assets = {};
  export let caption = '';
  export let video_resolved = null;

  // Get video URL from resolved assets or video_resolved
  $: videoAsset = video_resolved ||
                  Object.values(resolved_assets).find(a => a.asset_type === 'video') ||
                  {};
  $: videoSrc = videoAsset.src || '';
</script>

<div class="flex flex-col items-center justify-center h-full p-4">
  {#if videoSrc}
    <video
      src={videoSrc}
      controls
      class="max-w-full max-h-[80%] rounded-lg shadow-lg"
    >
      <track kind="captions" />
    </video>
  {:else}
    <div class="text-base-content/60 text-center">
      <p>Video not available</p>
    </div>
  {/if}
  {#if caption}
    <p class="mt-2 text-sm text-base-content/70 text-center">{caption}</p>
  {/if}
</div>
