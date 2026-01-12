<script>
  import { onMount } from 'svelte';
  import Hls from 'hls.js';

  export let streamUrl = '';        // HLS stream URL (from Episode.stream_url)
  export let slidesData = null;     // Slides array from API
  export let startTime = 0;         // N1: Initial seek position in seconds

  let videoElement;
  let presentationElement;
  let currentTime = 0;
  let paused = true;
  let hasSeekOnLoad = false;        // N1: Track if initial seek has been done
  let scriptsLoaded = false;        // Track when bp-web-components are ready

  // Format slides data for bp-slide-presentation
  // Only provide data after scripts are loaded to ensure custom elements are registered
  $: formattedData = (slidesData && scriptsLoaded) ? slidesData : null;

  // Theme is already in correct format from API (artwork.class, artwork.module, artwork.color)
  $: formattedTheme = slidesData?.theme ?? null;

  // Set data on the presentation element using setAttribute to ensure the converter runs
  $: if (presentationElement && formattedData) {
    presentationElement.setAttribute('data', JSON.stringify(formattedData));
  }

  // Set theme as a property (no attribute converter exists - must be set directly)
  $: if (presentationElement && formattedTheme) {
    presentationElement.theme = formattedTheme;
  }

  // Configure bp-web-components API URL BEFORE any scripts load
  // This must happen synchronously at module load time
  if (typeof window !== 'undefined') {
    window.__bp__ = window.__bp__ || { env: {} };
    window.__bp__.env = window.__bp__.env || {};
    window.__bp__.env.API_URL = '/api/bibleproject/graphql';
  }

  // Load bp-web-components dynamically with proper sequencing
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const existing = document.querySelector(`script[src="${src}"]`);
      if (existing) {
        // Script tag exists - resolve immediately (it may have already loaded)
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = src;
      script.type = 'module';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function loadBpComponents() {
    // Check if components are already registered (e.g., from previous navigation)
    if (customElements.get('bp-slide-presentation')) {
      scriptsLoaded = true;
      return;
    }

    try {
      // Load core first (registers bp-highlight and other base components)
      await loadScript('/bp/bp-core.js');
      // Then load slides (depends on core components)
      await loadScript('/bp/bp-slides.js');
      // Wait for key custom elements to be defined (with timeout fallback)
      await Promise.race([
        customElements.whenDefined('bp-slide-presentation'),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout waiting for bp-slide-presentation')), 5000))
      ]);
      scriptsLoaded = true;
    } catch (err) {
      console.error('Failed to load bp-web-components:', err);
      // Still try to proceed if elements are already defined
      if (customElements.get('bp-slide-presentation')) {
        scriptsLoaded = true;
      }
    }
  }

  onMount(() => {
    // Load bp-web-components scripts in sequence
    loadBpComponents().catch(err => console.error('Failed to load bp-web-components:', err));

    // Setup HLS video
    if (streamUrl && videoElement) {
      if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(streamUrl);
        hls.attachMedia(videoElement);

        // N1: Seek to startTime once video is loaded
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          if (startTime > 0 && !hasSeekOnLoad) {
            videoElement.currentTime = startTime;
            hasSeekOnLoad = true;
          }
        });
      } else if (videoElement.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        videoElement.src = streamUrl;

        // N1: Seek to startTime once video is loadedmetadata
        videoElement.addEventListener('loadedmetadata', () => {
          if (startTime > 0 && !hasSeekOnLoad) {
            videoElement.currentTime = startTime;
            hasSeekOnLoad = true;
          }
        }, { once: true });
      }
    }

    // Sync video time to presentation
    // Svelte reactivity handles updating the component via current-time={currentTime} binding
    const handleTimeUpdate = () => {
      currentTime = videoElement.currentTime;
      paused = videoElement.paused;
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

<div class="WatchView">
  <div class="WatchViewStage">
    <!-- Video pane -->
    <div class="WatchViewStagePane video-pane">
      <video
        bind:this={videoElement}
        controls
        playsinline
        controlslist="nodownload nofullscreen"
        crossorigin="anonymous"
      >
        <track kind="captions" />
      </video>
    </div>

    <!-- Slides pane -->
    <div class="WatchViewStagePane slides-pane">
      {#if formattedData}
        <bp-slide-presentation
          bind:this={presentationElement}
          current-time={currentTime}
          paused={paused}
          view-mode="default"
          decoration="box-shadow"
        ></bp-slide-presentation>
      {:else}
        <div class="loading-placeholder">
          Loading slides...
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Match BibleProject's WatchView layout */
  .WatchView {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    min-height: 0;
  }

  .WatchViewStage {
    display: flex;
    flex-direction: column;
    width: 100%;
    flex: 1;
    min-height: 0;
    gap: 1rem;
    padding: 1rem;
    box-sizing: border-box;
  }

  .WatchViewStagePane {
    flex: 1;
    width: 100%;
    min-height: 0;
    min-width: 0;
  }

  /* Video pane - maintains 16:9 with black background */
  .video-pane {
    display: flex;
    align-items: center;
    justify-content: center;
    background: #000;
    border-radius: 0.5rem;
    overflow: hidden;
  }

  .video-pane video {
    width: 100%;
    height: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  /* Slides pane - contains bp-slide-presentation */
  .slides-pane {
    display: flex;
    align-items: stretch;
    justify-content: center;
    background: var(--color-neutral-05, #f9fafc);
    border-radius: 0.5rem;
    /* Don't clip overflow - zoom animations need space to transition */
    overflow: visible;
    position: relative;
  }

  .slides-pane :global(bp-slide-presentation) {
    width: 100%;
    height: 100%;
    /* Ensure the component can expand for zoom animations */
    position: relative;
  }

  .loading-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: #6b7280;
  }

  /* Desktop layout: side-by-side when >= 1127px */
  /* BibleProject uses: min 555px per column + 17px separator = 1127px */
  @media (min-width: 1127px) {
    .WatchViewStage {
      flex-direction: row;
    }

    .WatchViewStagePane {
      flex: 1 1 0;
      min-width: 555px;
    }
  }
</style>
