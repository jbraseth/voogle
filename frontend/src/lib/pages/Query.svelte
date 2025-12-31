<script>
  import { onMount, tick } from "svelte";
  import CardQueryResult from '../CardQueryResult.svelte'
  import Player from '../Player.svelte'
  import ResultMap from '../ResultMap.svelte'
  import StretchSpinner from '../StretchSpinner.svelte'
  import {API_URL} from '../../api.js'
  import {channels} from '../../stores.js'
  export let qs;

  // receive query from url
  let query = qs.get("q")
  let queryLoading = false;
  let queryResults;
  let visualizationData = null;
  let visualizationLoading = false;
  let showVisualization = false;

  let selectedChannel;
  let player;
  let resultCards = [];

  async function doQuery(query) {
    if (query.length > 0) {
      queryLoading = true
      queryResults = false;
      visualizationData = null;
      history.replaceState(history.state, "", "?q=" + query);
      let params = new URLSearchParams({query_text: query, k: 6})
      if (selectedChannel) {
        params.set('channel_id', selectedChannel)
      }
      await fetch(`${API_URL}/media/query?${params}`).then(r => r.json()).then(data => {queryResults = data;});
      queryLoading = false

      // Fetch visualization data after results load (if enabled)
      if (showVisualization && queryResults && queryResults.length >= 2) {
        fetchVisualization(query);
      }
    }
  }

  async function fetchVisualization(queryText) {
    visualizationLoading = true;
    let params = new URLSearchParams({query_text: queryText, k: 20})
    if (selectedChannel) {
      params.set('channel_id', selectedChannel)
    }
    try {
      const response = await fetch(`${API_URL}/media/query/visualize?${params}`);
      if (response.ok) {
        visualizationData = await response.json();
      } else {
        visualizationData = null;
      }
    } catch (e) {
      console.error('Visualization fetch error:', e);
      visualizationData = null;
    }
    visualizationLoading = false;
  }

  function toggleVisualization() {
    showVisualization = !showVisualization;
    if (showVisualization && queryResults && queryResults.length >= 2 && !visualizationData) {
      fetchVisualization(query);
    }
  }

  function handlePointClick(event) {
    const { resultIndex } = event.detail;
    if (resultCards[resultIndex]) {
      resultCards[resultIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Add a brief highlight effect
      resultCards[resultIndex].classList.add('ring-2', 'ring-primary');
      setTimeout(() => {
        resultCards[resultIndex].classList.remove('ring-2', 'ring-primary');
      }, 2000);
    }
  }

  async function getChannels() {
    if($channels.length<1) {
      // TODO We should support more than 100 channels
      await fetch(`${API_URL}/media/channel?size=100`).then(r => r.json()).then(data => {$channels = data.items;});
    }
  }

  onMount(async () => {
    queryLoading = true
    await getChannels()
    if (query) {
      await doQuery(query)
    }
    queryLoading = false
  })

  let episodePlay;
  let channelPlay;
  let time;
  let mediaUrl;

  async function click(data) {
    episodePlay = data.detail.episode
    channelPlay = data.detail.channel
    time = data.detail.time
    mediaUrl = data.detail.media_url
    await tick()
    if (player) {
      player.scrollIntoView({ behavior: 'smooth' })
    }
  }

  function goToQuery(event) {
    if (event.key == 'Enter') {
      event.stopPropagation();
      event.preventDefault();
      doQuery(query)
    }
  }

  $: maxSim = queryResults ? queryResults[0].similarity : 1

</script>

<main class="flex flex-col grow pb-12 mt-6">
  <div class="grid grid-cols-1 md:grid-cols-4 mx-5 md:mx-16 gap-4">
    <textarea
      placeholder="Write your query..."
      class="textarea textarea-bordered h-16 text-lg md:col-span-2"
      bind:value={query}
      on:keypress={goToQuery}
      rows="1"
      data-testid="query-input"/>
    <select bind:value={selectedChannel} class="select select-bordered h-16">
      <option value={null} selected>All channels</option>
      {#each $channels as channel }
	<option value={channel.id}>{channel.title}</option>
      {/each}
    </select>
    <button class="btn h-16" on:click={doQuery(query)} data-testid="search-button">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-2">
	<path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
	<path stroke-linecap="round" stroke-linejoin="round" d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" />
      </svg>
      Search content
    </button>
  </div>
  <div class="mt-6 mx-5 md:mx-16 text-gray-500">
    ℹ️ Voogle will find related content in episodes
    transcriptions. Trying to find specific podcast episodes names
    won't be useful.
  </div>
  <div class="mt-2 mx-5 md:mx-16 text-gray-500">
    📢 We are happy to
    <a class="underline ml-1 mr-1" href="mailto:unmonoqueteclea@gmail.com"> receive</a>
    your feedback and podcasts requests.
  </div>

  <div class="mt-2 mx-5 md:mx-16 text-gray-500">
    🖤 Voogle doesn't offer any paid service.
    <a target="_blank" class="underline ml-1 mr-1" href="https://ko-fi.com/unmonoqueteclea">Help me</a>
    ensure the continued availability and accessibility of it.
  </div>

  <div class="flex flex-row place-content-center mt-1 mx-5 md:mx-16">
    <div class="divider w-full"></div>
  </div>
  {#if maxSim < 0.55}
  <div class="flex flex-row mt-2 mb-2 mx-5 md:mx-16 text-gray-500 font-semibold">
    🚩Low similarity scores, results may not be relevant. We add new
    episodes every day, try again in a few days.
  </div>
  {/if}
  {#if channelPlay}
    <div  bind:this="{player}" class="flex flex-row place-content-center mt-1 mx-5 md:mx-10">
      <Player time={time} channel={channelPlay} episode={episodePlay} media_url={mediaUrl}/>
    </div>
  {/if}
  {#if queryResults}
    <!-- Visualization toggle and map -->
    <div class="mx-5 md:mx-16 mt-4">
      <button
        class="btn btn-sm btn-outline gap-2"
        class:btn-active={showVisualization}
        on:click={toggleVisualization}
        data-testid="toggle-visualization">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
        </svg>
        {showVisualization ? 'Hide' : 'Show'} Result Map
      </button>

      {#if showVisualization}
        <ResultMap
          {visualizationData}
          loading={visualizationLoading}
          on:pointclick={handlePointClick} />
      {/if}
    </div>

    <div class="flex flex-row mt-6 mx-10">
      <div class="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 w-full">
	{#each queryResults as result, i }
	  <div bind:this={resultCards[i]} class="transition-all duration-300">
	    <CardQueryResult on:click={click} result={result} />
	  </div>
	{/each}
      </div>
    </div>
  {:else if queryLoading}
    <div class="flex flex-col grow items-center justify-center">
      <StretchSpinner size=100/>
      <p class="mt-8 text-lg">Searching related content...</p>
    </div>
  {:else}
    <div class="flex flex-col grow items-center justify-center text-center">
      <p class="lg:text-xl text-center text-gray-500">
	Write your <span class="font-semibold">query</span> in English
	🇺🇸 or Spanish 🇪🇸
      </p>
      <p class="lg:text-xl mt-2 text-gray-500">
	Related episodes fragments will appear here
      </p>
    </div>
  {/if}
</main>
