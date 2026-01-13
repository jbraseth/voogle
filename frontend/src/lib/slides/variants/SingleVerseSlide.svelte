<script>
  export let verseData = {};

  $: reference = verseData?.reference || '';
  $: text = verseData?.text || '';
</script>

<div class="flex flex-col items-center justify-center h-full p-8">
  <blockquote class="text-xl leading-relaxed text-center max-w-2xl">
    <p class="italic">{text}</p>
  </blockquote>
  {#if reference}
    <cite class="mt-4 text-base text-base-content/70 not-italic font-semibold">
      {reference}
    </cite>
  {/if}
</div>
