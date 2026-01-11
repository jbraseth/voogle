<script>
  import { onMount } from "svelte";
  import { API_URL } from '../api.js';
  import StretchSpinner from '../lib/StretchSpinner.svelte';

  let loading = true;
  let error = null;
  let courses = [];

  async function fetchCourses() {
    loading = true;
    error = null;
    try {
      const response = await fetch(`${API_URL}/bibleproject/courses`);
      if (!response.ok) {
        throw new Error(`Failed to fetch courses: ${response.status}`);
      }
      courses = await response.json();
    } catch (e) {
      console.error('Error fetching courses:', e);
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchCourses();
  });
</script>

<main class="flex flex-col grow gap-6 mt-6 px-8 mb-8">
  <div class="max-w-6xl mx-auto w-full">
    <h1 class="text-3xl font-bold mb-6">Courses</h1>

    {#if loading}
      <div class="flex flex-col items-center justify-center py-12">
        <StretchSpinner size={60} />
        <p class="mt-4 text-gray-500">Loading courses...</p>
      </div>
    {:else if error}
      <div class="flex flex-col items-center justify-center text-center py-12">
        <p class="text-error text-lg">{error}</p>
        <button class="btn btn-outline mt-4" on:click={fetchCourses}>Retry</button>
      </div>
    {:else if courses.length === 0}
      <div class="flex flex-col items-center justify-center text-center py-12">
        <p class="text-gray-500 text-lg">No courses available</p>
        <p class="text-gray-400 mt-2">Check the setup documentation to import BibleProject content.</p>
      </div>
    {:else}
      <div class="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {#each courses as course}
          <a
            href="/courses/{course.slug}"
            class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer"
          >
            {#if course.image}
              <figure class="h-48 overflow-hidden">
                <img
                  src={course.image}
                  alt={course.title}
                  class="w-full h-full object-cover"
                />
              </figure>
            {:else}
              <figure class="h-48 bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <span class="text-4xl opacity-50">📖</span>
              </figure>
            {/if}
            <div class="card-body">
              <h2 class="card-title">{course.title}</h2>
              <p class="text-gray-500">
                {course.session_count} {course.session_count === 1 ? 'session' : 'sessions'}
              </p>
            </div>
          </a>
        {/each}
      </div>
    {/if}
  </div>
</main>
