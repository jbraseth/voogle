<script>
  import Hls from 'hls.js';
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';

  export let src = '';
  export let startTime = 0;
  export let poster = '';

  export let currentTime = 0;
  export let duration = 0;
  export let paused = true;
  export let playing = false;

  const dispatch = createEventDispatcher();

  let mediaElement;
  let hls = null;
  let hasStarted = false;

  $: isHls = src && src.includes('.m3u8');

  function setupHls() {
    if (!mediaElement || !src) return;

    if (hls) {
      hls.destroy();
      hls = null;
    }

    if (isHls) {
      if (Hls.isSupported()) {
        hls = new Hls();
        hls.loadSource(src);
        hls.attachMedia(mediaElement);
      } else if (mediaElement.canPlayType('application/vnd.apple.mpegurl')) {
        mediaElement.src = src;
      }
    } else {
      mediaElement.src = src;
    }
  }

  onMount(() => {
    setupHls();
  });

  onDestroy(() => {
    if (hls) {
      hls.destroy();
      hls = null;
    }
  });

  $: if (mediaElement && src) {
    hasStarted = false;
    setupHls();
  }

  function handleTimeUpdate() {
    currentTime = mediaElement.currentTime;
    dispatch('timeupdate', { currentTime });
  }

  function handlePlay() {
    paused = false;
    playing = true;
    dispatch('play');
  }

  function handlePause() {
    paused = true;
    playing = false;
    dispatch('pause');
  }

  function handleEnded() {
    paused = true;
    playing = false;
    dispatch('ended');
  }

  function handleCanPlay() {
    duration = mediaElement.duration;
    if (!hasStarted && startTime > 0) {
      mediaElement.currentTime = startTime;
      hasStarted = true;
    }
    dispatch('canplay', { duration });
  }

  function handleDurationChange() {
    duration = mediaElement.duration;
  }
</script>

{#if isHls}
  <video
    bind:this={mediaElement}
    {poster}
    controls
    class="w-full"
    on:timeupdate={handleTimeUpdate}
    on:play={handlePlay}
    on:pause={handlePause}
    on:ended={handleEnded}
    on:canplay={handleCanPlay}
    on:durationchange={handleDurationChange}
  >
    <track kind="captions" />
  </video>
{:else}
  <audio
    bind:this={mediaElement}
    controls
    class="w-full"
    on:timeupdate={handleTimeUpdate}
    on:play={handlePlay}
    on:pause={handlePause}
    on:ended={handleEnded}
    on:canplay={handleCanPlay}
    on:durationchange={handleDurationChange}
  />
{/if}

<style>
  video, audio {
    width: 100%;
    max-width: 100%;
  }
</style>
