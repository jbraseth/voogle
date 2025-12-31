<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';

  export let visualizationData = null;
  export let loading = false;

  const dispatch = createEventDispatcher();

  let plotContainer;
  let Plotly = null;
  let plotlyLoaded = false;

  // Lazy load Plotly
  async function loadPlotly() {
    if (Plotly) return Plotly;
    try {
      const module = await import('plotly.js-dist-min');
      Plotly = module.default;
      plotlyLoaded = true;
      return Plotly;
    } catch (e) {
      console.error('Failed to load Plotly:', e);
      return null;
    }
  }

  function getColorByScore(score) {
    // Map score 0-1 to green gradient
    const r = Math.round(255 * (1 - score));
    const g = Math.round(180 + 75 * score);
    const b = Math.round(100 * (1 - score));
    return `rgb(${r},${g},${b})`;
  }

  async function renderPlot() {
    if (!visualizationData || !plotContainer) return;

    const plt = await loadPlotly();
    if (!plt) return;

    const { points, query_point } = visualizationData;

    // Result points trace
    const resultTrace = {
      x: points.map(p => p.x),
      y: points.map(p => p.y),
      mode: 'markers',
      type: 'scatter',
      name: 'Results',
      marker: {
        size: 12,
        color: points.map(p => getColorByScore(p.score)),
        line: { width: 1, color: 'rgba(0,0,0,0.3)' }
      },
      text: points.map(p => p.preview),
      hovertemplate: '<b>%{text}</b><br>Score: %{customdata:.0%}<extra></extra>',
      customdata: points.map(p => p.score),
    };

    // Query point trace
    const queryTrace = {
      x: [query_point.x],
      y: [query_point.y],
      mode: 'markers',
      type: 'scatter',
      name: 'Your Search',
      marker: {
        size: 16,
        color: '#3b82f6',
        symbol: 'star',
        line: { width: 2, color: '#1d4ed8' }
      },
      text: [query_point.label],
      hovertemplate: '<b>%{text}</b><extra></extra>',
    };

    const layout = {
      showlegend: true,
      legend: {
        x: 0,
        y: 1,
        bgcolor: 'rgba(255,255,255,0.8)'
      },
      margin: { l: 40, r: 20, t: 20, b: 40 },
      xaxis: { showgrid: true, zeroline: false, title: '' },
      yaxis: { showgrid: true, zeroline: false, title: '' },
      hovermode: 'closest',
      dragmode: 'pan',
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
      displaylogo: false,
    };

    plt.newPlot(plotContainer, [resultTrace, queryTrace], layout, config);

    // Handle click events
    plotContainer.on('plotly_click', function(data) {
      if (data.points && data.points.length > 0) {
        const point = data.points[0];
        // Only handle clicks on result points (trace 0), not query point
        if (point.curveNumber === 0) {
          const resultIndex = point.pointIndex;
          dispatch('pointclick', { resultIndex });
        }
      }
    });
  }

  // Reactively render when data changes
  $: if (visualizationData && plotContainer && !loading) {
    renderPlot();
  }

  onMount(() => {
    loadPlotly();
  });

  onDestroy(() => {
    if (Plotly && plotContainer) {
      Plotly.purge(plotContainer);
    }
  });
</script>

<div class="result-map-container">
  {#if loading}
    <div class="flex items-center justify-center h-64 bg-base-200 rounded-lg">
      <span class="loading loading-spinner loading-lg"></span>
      <span class="ml-3">Loading visualization...</span>
    </div>
  {:else if visualizationData && visualizationData.points.length >= 2}
    <div class="bg-base-100 rounded-lg shadow p-2">
      <div class="text-sm text-gray-500 mb-2 px-2">
        Click a point to jump to that result. Points closer together are semantically similar.
      </div>
      <div bind:this={plotContainer} class="w-full h-64 md:h-80"></div>
    </div>
  {:else if visualizationData && visualizationData.points.length < 2}
    <div class="alert alert-info">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span>Not enough results to visualize. Need at least 2 results for the map.</span>
    </div>
  {/if}
</div>

<style>
  .result-map-container {
    margin-top: 1rem;
    margin-bottom: 1rem;
  }
</style>
