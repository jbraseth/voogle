<script>
  import { onMount } from 'svelte';
  import Hls from 'hls.js';

  export let streamUrl = '';        // HLS stream URL (from Episode.stream_url)
  export let slidesData = null;     // Slides array from API

  let videoElement;
  let presentationElement;
  let currentTime = 0;
  let paused = true;

  // Format slides data for bp-slide-presentation
  // The component expects { presentationSlides: [...] } or array with config field
  $: formattedData = slidesData ? JSON.stringify(slidesData) : null;

  onMount(() => {
    // Load bp-web-components (side effect: registers custom elements)
    import('/bp/bp-slides.js');
    import('/bp/bp-core.js');

    // Setup HLS video
    if (streamUrl && videoElement) {
      if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(streamUrl);
        hls.attachMedia(videoElement);
      } else if (videoElement.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        videoElement.src = streamUrl;
      }
    }

    // Sync video time to presentation
    const handleTimeUpdate = () => {
      currentTime = videoElement.currentTime;
      paused = videoElement.paused;

      if (presentationElement) {
        presentationElement.setAttribute('current-time', currentTime.toString());
        presentationElement.setAttribute('paused', paused.toString());
      }
    };

    videoElement?.addEventListener('timeupdate', handleTimeUpdate);
    videoElement?.addEventListener('play', handleTimeUpdate);
    videoElement?.addEventListener('pause', handleTimeUpdate);

    return () => {
      videoElement?.removeEventListener('timeupdate', handleTimeUpdate);
      videoElement?.removeEventListener('play', handleTimeUpdate);
      videoElement?.removeEventListener('pause', handleTimeUpdate);
    };
  });
</script>

<svelte:head>
  <link rel="stylesheet" href="/bp/theme.css" />
  <link rel="stylesheet" href="/bp/bp.css" />
</svelte:head>

<div class="bible-project-player">
  <div class="video-panel">
    <video
      bind:this={videoElement}
      controls
      class="w-full h-full"
    >
      <track kind="captions" />
    </video>
  </div>

  <div class="slide-panel">
    {#if formattedData}
      <bp-slide-presentation
        bind:this={presentationElement}
        data={formattedData}
        current-time={currentTime}
        paused={paused}
      ></bp-slide-presentation>
    {:else}
      <div class="flex items-center justify-center h-full text-gray-500">
        Loading slides...
      </div>
    {/if}
  </div>
</div>

<style>
  .bible-project-player {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    height: 100%;
    min-height: 500px;
  }

  .video-panel {
    background: #000;
    border-radius: 0.5rem;
    overflow: hidden;
  }

  .slide-panel {
    background: var(--color-neutral-05, #f9fafc);
    border-radius: 0.5rem;
    overflow: hidden;
  }

  /* Ensure bp-slide-presentation fills container */
  .slide-panel :global(bp-slide-presentation) {
    display: block;
    width: 100%;
    height: 100%;
  }

  @media (max-width: 768px) {
    .bible-project-player {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }
  }
</style>
