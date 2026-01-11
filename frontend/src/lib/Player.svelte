<script>
  import MediaPlayer from './MediaPlayer.svelte';
  import BibleProjectPlayer from './BibleProjectPlayer.svelte';
  import WaveSpinner from './WaveSpinner.svelte'
  import {API_URL, API_ORIGIN} from '../api.js'

  export let channel;
  export let episode;
  export let time;
  export let media_url;

  let isWaiting = false;
  let currentTime = 0;
  let duration = 0;
  let paused = true;
  let playing = false;
  let slidesData = null;

  // Check if this is a BibleProject episode
  $: isBibleProject = channel?.kind === 'bibleproject';

  // Get stream URL for BibleProject (from episode.stream_url or construct from mux_playback_id)
  $: streamUrl = episode?.stream_url || (episode?.mux_playback_id ? `https://stream.mux.com/${episode.mux_playback_id}.m3u8` : null);

  // Fetch slides data for BibleProject episodes
  $: if (isBibleProject && episode) {
    fetchSlides(episode);
  }

  async function fetchSlides(ep) {
    // Extract course and session from episode guid
    // guid format: "bibleproject:ephesians:1"
    const parts = ep.guid.split(':');
    if (parts.length >= 3) {
      const course = parts[1];
      const session = parts[2];
      try {
        const response = await fetch(`${API_URL}/bibleproject/slides/${course}/${session}`);
        if (response.ok) {
          slidesData = await response.json();
        }
      } catch (e) {
        console.error('Failed to fetch slides:', e);
      }
    }
  }

  function resolveMediaUrl(url) {
    if (url && url.startsWith('/local/')) {
      return API_ORIGIN + url;
    }
    return url;
  }

  $: {
    isWaiting = !!episode;
  }

  $: edate = new Date(episode.date);
  $: resolvedUrl = resolveMediaUrl(media_url);

  function handleCanPlay() {
    isWaiting = false;
  }
</script>
{#if isBibleProject}
  <BibleProjectPlayer {streamUrl} {slidesData} />
{:else}
  <div class="card w-full h-80 sm:h-64 lg:h-40 bg-base-100 shadow-xl image-full" data-testid="audio-player-active">
    <img class="object-cover w-full h-full" src="{channel.image}"  />
    <div class="grid grid-cols-2 lg:grid-cols-3 card-body">
      <div class="col-span-2 flex flex-col">
        <h2 class="card-title line-clamp-1">{ channel.title }</h2>
        <p class="max-h-32 line-clamp-3">{episode.title}</p>
        <div class="flex flex-row mt-0">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 mr-1 mt-2">
            <path fill-rule="evenodd" d="M6.75 2.25A.75.75 0 017.5 3v1.5h9V3A.75.75 0 0118 3v1.5h.75a3 3 0 013 3v11.25a3 3 0 01-3 3H5.25a3 3 0 01-3-3V7.5a3 3 0 013-3H6V3a.75.75 0 01.75-.75zm13.5 9a1.5 1.5 0 00-1.5-1.5H5.25a1.5 1.5 0 00-1.5 1.5v7.5a1.5 1.5 0 001.5 1.5h13.5a1.5 1.5 0 001.5-1.5v-7.5z" clip-rule="evenodd" />
          </svg>
          <p class="text-md mt-1 ml-1">
            { edate.toDateString() }
          </p>
        </div>
      </div>
      <div class="mx-8 col-span-2 mt-5 lg:mt-0 lg:col-span-1">
        {#if isWaiting}
        <WaveSpinner size=80/>
        {/if}
        <div class="{ isWaiting ? 'invisible' : 'visible'}">
          <MediaPlayer
            src={resolvedUrl}
            startTime={time}
            bind:currentTime
            bind:duration
            bind:paused
            bind:playing
            on:canplay={handleCanPlay}
          />
        </div>
      </div>
    </div>
  </div>
{/if}
