<script>
  import { onMount } from "svelte";
  import { API_URL } from '../api.js';
  import StretchSpinner from '../lib/StretchSpinner.svelte';
  import BibleProjectPlayer from '../lib/BibleProjectPlayer.svelte';

  export let course = '';
  export let sessionId = '';

  let loading = true;
  let error = null;
  let episode = null;
  let slidesData = null;

  // S4: Read start time from URL query parameter (?t=seconds)
  let startTime = 0;

  async function fetchSession() {
    if (!course || !sessionId) return;

    loading = true;
    error = null;
    try {
      // Fetch episode info
      const episodeResponse = await fetch(`${API_URL}/bibleproject/episodes/${course}/${sessionId}`);
      if (!episodeResponse.ok) {
        throw new Error(`Failed to fetch session: ${episodeResponse.status}`);
      }
      episode = await episodeResponse.json();

      // Fetch slides data
      const slidesResponse = await fetch(`${API_URL}/bibleproject/slides/${course}/${sessionId}`);
      if (slidesResponse.ok) {
        slidesData = await slidesResponse.json();
      }
    } catch (e) {
      console.error('Error fetching session:', e);
      error = e.message;
    } finally {
      loading = false;
    }
  }

  // Get stream URL from episode
  $: streamUrl = episode && episode.mux_playback_id
    ? `https://stream.mux.com/${episode.mux_playback_id}.m3u8`
    : null;

  onMount(() => {
    // S4: Parse start time from URL query param
    const urlParams = new URLSearchParams(window.location.search);
    startTime = parseInt(urlParams.get('t') || '0', 10);

    fetchSession();
  });
</script>

<main class="flex flex-col grow gap-6 mt-6 px-8 mb-8">
  <div class="max-w-6xl mx-auto w-full">
    <a href="/courses/{course}" class="btn btn-ghost btn-sm mb-4">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to Course
    </a>

    {#if loading}
      <div class="flex flex-col items-center justify-center py-12">
        <StretchSpinner size={60} />
        <p class="mt-4 text-gray-500">Loading session...</p>
      </div>
    {:else if error}
      <div class="flex flex-col items-center justify-center text-center py-12">
        <p class="text-error text-lg">{error}</p>
        <a href="/courses/{course}" class="btn btn-outline mt-4">Back to Course</a>
      </div>
    {:else if episode}
      <div class="mb-4">
        <h1 class="text-2xl font-bold mb-2">{episode.title}</h1>
        {#if episode.description}
          <p class="text-gray-600">{episode.description}</p>
        {/if}
      </div>

      {#if streamUrl && slidesData}
        <BibleProjectPlayer
          {streamUrl}
          {slidesData}
          {startTime}
        />
      {:else if streamUrl}
        <div class="video-container rounded-lg overflow-hidden bg-black">
          <video controls class="w-full max-h-[70vh]">
            <source src={streamUrl} type="application/vnd.apple.mpegurl" />
            <track kind="captions" />
            Your browser does not support HLS video playback.
          </video>
        </div>
      {:else}
        <p class="text-gray-500">No video available for this session.</p>
      {/if}
    {:else}
      <div class="flex flex-col items-center justify-center text-center py-12">
        <p class="text-gray-500 text-lg">Session not found</p>
        <a href="/courses/{course}" class="btn btn-outline mt-4">Back to Course</a>
      </div>
    {/if}
  </div>
</main>
