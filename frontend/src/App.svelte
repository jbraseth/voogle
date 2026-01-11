<script>
  import router from "page"
  import {routes, parseqs, getPageNum, getEpisodeIdFromPath, getSlugFromPath, getSessionParamsFromPath} from "./routes.js";
  import PageHeader from './lib/PageHeader.svelte'
  import PageFooter from './lib/PageFooter.svelte'

  // routing configuration
  let pagenum = -1;
  let page;
  let qs;
  let episodeId = null;
  let slug = null;
  let course = null;
  let sessionId = null;

  router('*', parseqs)
  routes.forEach(route => {
    router(
      route.path,
      (ctx, next) => {
	pagenum = getPageNum(ctx.pathname);
	qs = ctx.qs;
	// N1: Extract episodeId from path for content routes
	episodeId = getEpisodeIdFromPath(ctx.pathname);
	// N2: Extract slug for course detail routes
	slug = getSlugFromPath(ctx.pathname);
	// N2: Extract course and sessionId for session routes
	const sessionParams = getSessionParamsFromPath(ctx.pathname);
	course = sessionParams?.course ?? null;
	sessionId = sessionParams?.sessionId ?? null;
	next();
      },
      () => {page = route.component;}
    );
  });
  router.start();
</script>

<div class="flex flex-col min-h-screen">
  <PageHeader selected={pagenum} />
  <svelte:component this={page} qs={qs} {episodeId} {slug} {course} {sessionId}/>
  <PageFooter/>
</div>
