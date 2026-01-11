<script>
  import { onMount } from "svelte";
  import { API_URL } from '../api.js';
  import StretchSpinner from '../lib/StretchSpinner.svelte';

  export let slug = '';

  let loading = true;
  let error = null;
  let course = null;

  function formatDuration(seconds) {
    if (!seconds) return '';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  async function fetchCourse() {
    if (!slug) return;

    loading = true;
    error = null;
    try {
      const response = await fetch(`${API_URL}/bibleproject/courses/${slug}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch course: ${response.status}`);
      }
      course = await response.json();
    } catch (e) {
      console.error('Error fetching course:', e);
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchCourse();
  });
</script>

<main class="flex flex-col grow gap-6 mt-6 px-8 mb-8">
  <div class="max-w-4xl mx-auto w-full">
    <a href="/courses" class="btn btn-ghost btn-sm mb-4">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to Courses
    </a>

    {#if loading}
      <div class="flex flex-col items-center justify-center py-12">
        <StretchSpinner size={60} />
        <p class="mt-4 text-gray-500">Loading course...</p>
      </div>
    {:else if error}
      <div class="flex flex-col items-center justify-center text-center py-12">
        <p class="text-error text-lg">{error}</p>
        <a href="/courses" class="btn btn-outline mt-4">Back to Courses</a>
      </div>
    {:else if course}
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">{course.title}</h1>
        {#if course.description}
          <p class="text-gray-600">{course.description}</p>
        {/if}
      </div>

      {#if course.sessions && course.sessions.length > 0}
        <div class="space-y-3">
          {#each course.sessions as session, index}
            <a
              href="/session/{slug}/{session.id}"
              class="card bg-base-100 shadow hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div class="card-body py-4 px-6 flex-row items-center justify-between">
                <div class="flex items-center gap-4">
                  <span class="text-lg font-medium text-gray-400 w-8">{index + 1}</span>
                  <div>
                    <h3 class="font-medium">{session.title}</h3>
                    {#if session.duration}
                      <p class="text-sm text-gray-500">{formatDuration(session.duration)}</p>
                    {/if}
                  </div>
                </div>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </a>
          {/each}
        </div>
      {:else}
        <div class="text-center py-12">
          <p class="text-gray-500">No sessions available for this course.</p>
        </div>
      {/if}
    {:else}
      <div class="flex flex-col items-center justify-center text-center py-12">
        <p class="text-gray-500 text-lg">Course not found</p>
        <a href="/courses" class="btn btn-outline mt-4">Back to Courses</a>
      </div>
    {/if}
  </div>
</main>
