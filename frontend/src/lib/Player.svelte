<script>
  import MediaPlayer from './MediaPlayer.svelte';
  import WaveSpinner from './WaveSpinner.svelte'
  import {API_ORIGIN} from '../api.js'

  export let channel;
  export let episode;
  export let time;
  export let media_url;

  let isWaiting = false;
  let currentTime = 0;
  let duration = 0;
  let paused = true;
  let playing = false;

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
