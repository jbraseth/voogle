<script>
  import { onMount } from "svelte";
  import {API_URL} from '../../api.js'
  import StretchSpinner from '../StretchSpinner.svelte'
  import BibleProjectPlayer from '../BibleProjectPlayer.svelte'

  export let qs;
  export let episodeId = null;

  let loading = false;
  let error = null;
  let episode = null;
  let channel = null;
  let slidesData = null;
  let startTime = 0;

  // N1: Parse start timestamp from query param
  $: startTime = qs && qs.get("t") ? parseInt(qs.get("t"), 10) : 0;

  // N1: Parse course slug and session ID from episode guid
  function parseBibleProjectGuid(guid) {
    if (!guid || !guid.startsWith('bibleproject:')) {
      return null;
    }
    const parts = guid.split(':');
    if (parts.length >= 3) {
      return {
        courseSlug: parts[1],
        sessionId: parts[2]
      };
    }
    return null;
  }

  async function fetchEpisode() {
    if (!episodeId) return;

    loading = true;
    error = null;

    try {
      // N1: Use public episode detail endpoint
      const response = await fetch(`${API_URL}/media/episode/${episodeId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch episode: ${response.status}`);
      }
      episode = await response.json();

      // Parse BibleProject guid for slides
      const bpInfo = parseBibleProjectGuid(episode.guid);
      if (bpInfo) {
        await fetchSlides(bpInfo.courseSlug, bpInfo.sessionId);
      }
    } catch (e) {
      console.error('Error fetching episode:', e);
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function fetchSlides(courseSlug, sessionId) {
    try {
      const response = await fetch(`${API_URL}/bibleproject/slides/${courseSlug}/${sessionId}`);
      if (response.ok) {
        slidesData = await response.json();
      }
    } catch (e) {
      console.error('Error fetching slides:', e);
      // Non-fatal: slides just won't show
    }
  }

  // Get stream URL from episode
  $: streamUrl = episode && episode.mux_playback_id
    ? `https://stream.mux.com/${episode.mux_playback_id}.m3u8`
    : null;

  onMount(() => {
    if (episodeId) {
      fetchEpisode();
    }
  });

  // N1: If no episodeId, show original content listing
  let queryLoading = false;
  let queryResults = [];

  async function doQuery() {
    queryLoading = true
    queryResults = [];
    let url = new URL(API_URL + "/analytics/media-count")
    await fetch(url).then(r => r.json()).then(data => {queryResults = data.channels;});
    queryLoading = false
  }

  $: channels = queryResults.filter((c) => c.available_episodes > 0);

  onMount(async () => {
    if (!episodeId) {
      await doQuery();
    }
  });
</script>

{#if episodeId}
  <!-- N1: Episode detail view with BibleProjectPlayer -->
  <main class="flex flex-col grow gap-6 mt-6 px-8 mb-8">
    {#if loading}
      <div class="flex flex-col grow items-center justify-center">
        <StretchSpinner size=60/>
        <p class="mt-4 text-gray-500">Loading episode...</p>
      </div>
    {:else if error}
      <div class="flex flex-col items-center justify-center text-center">
        <p class="text-error text-lg">{error}</p>
        <a href="/query" class="btn btn-outline mt-4">Back to Search</a>
      </div>
    {:else if episode}
      <div class="max-w-6xl mx-auto w-full">
        <h1 class="text-2xl font-bold mb-2">{episode.title}</h1>
        {#if episode.description}
          <p class="text-gray-600 mb-4">{episode.description}</p>
        {/if}

        {#if streamUrl && slidesData}
          <BibleProjectPlayer
            {streamUrl}
            {slidesData}
            {startTime}
          />
        {:else if streamUrl}
          <div class="video-container">
            <video controls class="w-full max-h-[70vh]">
              <source src={streamUrl} type="application/vnd.apple.mpegurl" />
              <track kind="captions" />
              Your browser does not support HLS video playback.
            </video>
          </div>
        {:else}
          <p class="text-gray-500">No video available for this episode.</p>
        {/if}
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center text-center">
        <p class="text-gray-500 text-lg">Episode not found</p>
        <a href="/query" class="btn btn-outline mt-4">Back to Search</a>
      </div>
    {/if}
  </main>
{:else}
  <!-- Original content listing view -->
  <main class="flex flex-col grow gap-12 lg:mt-6 px-8 mb-8 items-center">
    <div class="flex flex-col items-center">
      <h2 class="text-2xl font-bold max-w-2xl text-center">
        These are all the podcasts available
      </h2>
      <p class="mt-2 text-xl max-w-2xl text-center">
        The list grows every day!
      </p>
    </div>
    {#if channels.length > 0}
      <div class="grid gap-12 grid-cols-1 md:grid-cols-2 xl:grid-cols-3 w-full lg:px-8">
        <!-- episode collection card -->
        {#each channels as channel}
          <div class="card shadow-xl card-side">
            <figure>
              <img class="object-fit h-full w-28 md:w-44" src="{channel.image}" alt="{channel.title}" />
            </figure>
            <div class="card-body">
              <a href="{channel.url}">
                <h2 class="line-clamp-3 card-title text-base">{channel.title}</h2>
              </a>
              <p><span class="font-semibold">{channel.available_episodes}</span> episodes available.
              </p>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="flex flex-col grow items-center justify-center">
        <StretchSpinner size=60/>
      </div>
    {/if}
    <div>
      <p class="mt-6 max-w-2xl text-center">
        Do you want to index your own content? Are you a content creator
        and want to offer full transcriptions and automatically
        generated summaries to your subscribers?
      </p>
      <p class="mt-2 max-w-2xl text-center">
        Check <a class="ml-1 underline" href="/pro">Voogle PRO</a>.
      </p>
    </div>
  </main>
{/if}
