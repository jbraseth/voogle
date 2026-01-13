<script>
  import { onMount } from 'svelte';
  import MediaPlayer from '../MediaPlayer.svelte';
  import SlidePanel from '../slides/SlidePanel.svelte';

  let course = 'abraham';
  let sessionId = '1';
  let slides = [];
  let currentTime = 0;
  let loading = true;
  let error = null;
  let videoSrc = '';
  let rawData = null;

  onMount(async () => {
    await loadSession();
  });

  async function loadSession() {
    loading = true;
    error = null;
    try {
      const res = await fetch(`/api/bibleproject/slides/${course}/${sessionId}`);
      if (!res.ok) throw new Error(`Failed to load slides: ${res.status}`);
      rawData = await res.json();

      // Transform API slides to component format
      // API structure: { content: { variant, content: {...actualData}, timestamp, ... }, resolved_assets }
      slides = rawData.slides.map((s, idx) => ({
        timestamp: s.content?.timestamp || idx * 30,
        variant: s.content?.variant || 'paragraph',
        content: s.content?.content || s.content || {},  // Flatten nested content
        resolved_assets: s.resolved_assets || {}
      }));

      // Try to get playback_id from session metadata
      if (rawData.playback_id) {
        videoSrc = `https://stream.mux.com/${rawData.playback_id}.m3u8`;
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function handleTimeUpdate(e) {
    currentTime = e.detail.currentTime;
  }

  function handleSeek(e) {
    currentTime = e.detail.timestamp;
  }
</script>

<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">BibleProject Component Test</h1>

  <div class="flex gap-4 mb-4">
    <input
      type="text"
      bind:value={course}
      placeholder="Course slug"
      class="input input-bordered"
    />
    <input
      type="text"
      bind:value={sessionId}
      placeholder="Session ID"
      class="input input-bordered w-20"
    />
    <button class="btn btn-primary" on:click={loadSession}>Load</button>
  </div>

  {#if loading}
    <div class="flex justify-center p-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if error}
    <div class="alert alert-error">
      <span>{error}</span>
    </div>
  {:else}
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Video Player -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">MediaPlayer (P1)</h2>
          <div class="mb-2">
            <input
              type="text"
              bind:value={videoSrc}
              placeholder="https://stream.mux.com/PLAYBACK_ID.m3u8"
              class="input input-bordered w-full text-sm"
            />
          </div>
          {#if videoSrc}
            <MediaPlayer
              src={videoSrc}
              on:timeupdate={handleTimeUpdate}
            />
          {:else}
            <div class="bg-base-200 rounded-lg p-8 text-center">
              <p>Enter a Mux HLS URL above to test video</p>
            </div>
          {/if}
          <p class="text-sm opacity-60">Current time: {currentTime.toFixed(1)}s</p>
        </div>
      </div>

      <!-- Slide Panel -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">SlidePanel (P2)</h2>
          <p class="text-sm opacity-60 mb-2">{slides.length} slides loaded</p>
          <div class="h-96">
            <SlidePanel
              {slides}
              {currentTime}
              on:seek={handleSeek}
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Debug: Raw slide data -->
    <details class="mt-4">
      <summary class="cursor-pointer text-sm opacity-60">Debug: Raw API response</summary>
      <pre class="text-xs bg-base-200 p-4 rounded overflow-auto max-h-96">{JSON.stringify(rawData, null, 2)}</pre>
    </details>
  {/if}
</div>
