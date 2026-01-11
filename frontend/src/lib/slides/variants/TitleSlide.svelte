<script>
  export let className = '';
  export let sessionNumber = '';
  export let sessionName = '';
  export let teacherName = '';
</script>

<div class="flex flex-col items-center justify-center h-full p-8 text-center">
  {#if className}
    <p class="text-lg text-base-content/70 uppercase tracking-wider mb-2">{className}</p>
  {/if}
  {#if sessionNumber}
    <p class="text-sm text-base-content/60 mb-4">Session {sessionNumber}</p>
  {/if}
  <h1 class="text-3xl md:text-4xl font-bold text-base-content mb-6">{sessionName}</h1>
  {#if teacherName}
    <p class="text-lg text-base-content/80">{teacherName}</p>
  {/if}
</div>
