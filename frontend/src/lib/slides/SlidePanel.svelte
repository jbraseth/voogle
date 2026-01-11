<script>
  import { createEventDispatcher } from 'svelte';
  import SlideRenderer from './SlideRenderer.svelte';

  export let slides = [];
  export let currentTime = 0;

  const dispatch = createEventDispatcher();

  $: currentSlideIndex = computeCurrentSlideIndex(slides, currentTime);

  function computeCurrentSlideIndex(slides, time) {
    if (!slides || slides.length === 0) return -1;

    let index = 0;
    for (let i = 0; i < slides.length; i++) {
      if (slides[i].timestamp <= time) {
        index = i;
      } else {
        break;
      }
    }
    return index;
  }

  $: currentSlide = currentSlideIndex >= 0 ? slides[currentSlideIndex] : null;

  function handleThumbnailClick(index) {
    if (slides[index]) {
      dispatch('seek', { timestamp: slides[index].timestamp });
    }
  }
</script>

<div class="flex flex-col h-full">
  <!-- Current slide display -->
  <div class="flex-1 min-h-0">
    {#if currentSlide}
      <SlideRenderer slide={currentSlide} />
    {:else}
      <div class="flex items-center justify-center h-full bg-base-200 rounded-lg">
        <p class="text-base-content/60">No slides available</p>
      </div>
    {/if}
  </div>

  <!-- Thumbnail strip -->
  {#if slides && slides.length > 0}
    <div class="mt-4 overflow-x-auto">
      <div class="flex gap-2 pb-2">
        {#each slides as slide, index}
          <button
            class="flex-shrink-0 w-24 h-16 rounded border-2 overflow-hidden transition-all
                   {index === currentSlideIndex ? 'border-primary ring-2 ring-primary/30' : 'border-base-300 hover:border-primary/50'}"
            on:click={() => handleThumbnailClick(index)}
            title="Go to slide {index + 1}"
          >
            <div class="w-full h-full transform scale-[0.25] origin-top-left" style="width: 400%; height: 400%;">
              <SlideRenderer {slide} />
            </div>
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>
