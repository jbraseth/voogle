<script>
  import TitleSlide from './variants/TitleSlide.svelte';
  import MainPointSlide from './variants/MainPointSlide.svelte';
  import WordDefinitionSlide from './variants/WordDefinitionSlide.svelte';
  import ParagraphSlide from './variants/ParagraphSlide.svelte';
  import ScriptureSlide from './variants/ScriptureSlide.svelte';
  import QuestionSlide from './variants/QuestionSlide.svelte';
  import DiagramSlide from './variants/DiagramSlide.svelte';
  import ImageSlide from './variants/ImageSlide.svelte';
  import TableSlide from './variants/TableSlide.svelte';
  import ThankYouSlide from './variants/ThankYouSlide.svelte';

  export let slide = {};

  $: variant = slide?.variant || '';
  $: content = slide?.content || {};
  $: resolved_assets = slide?.resolved_assets || {};
</script>

<div class="w-full h-full bg-base-200 rounded-lg">
  {#if variant === 'title'}
    <TitleSlide
      className={content.className}
      sessionNumber={content.sessionNumber}
      sessionName={content.sessionName}
      teacherName={content.teacherName}
    />
  {:else if variant === 'main_point'}
    <MainPointSlide content={content.text || content.content} />
  {:else if variant === 'word_definition'}
    <WordDefinitionSlide wordDefinitionData={content.wordDefinitionData || []} />
  {:else if variant === 'paragraph'}
    <ParagraphSlide title={content.title} content={content.content} />
  {:else if variant === 'scripture' || variant === 'scripture_single' || variant === 'scripture_multi'}
    <ScriptureSlide
      reference={content.reference}
      text={content.text}
      verses={content.verses}
    />
  {:else if variant === 'question'}
    <QuestionSlide question={content.question || content.text} />
  {:else if variant === 'diagram'}
    <DiagramSlide {resolved_assets} caption={content.caption} />
  {:else if variant === 'image'}
    <ImageSlide {resolved_assets} caption={content.caption} />
  {:else if variant === 'table'}
    <TableSlide body={content.body} title={content.title} />
  {:else if variant === 'thank_you'}
    <ThankYouSlide message={content.message} />
  {:else}
    <div class="flex items-center justify-center h-full p-8">
      <p class="text-base-content/60 text-center">Unknown slide type: {variant}</p>
    </div>
  {/if}
</div>
