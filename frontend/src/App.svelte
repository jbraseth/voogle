<script>
  import router from "page"
  import {routes, parseqs, getPageNum, getEpisodeIdFromPath} from "./routes.js";
  import PageHeader from './lib/PageHeader.svelte'
  import PageFooter from './lib/PageFooter.svelte'

  // routing configuration
  let pagenum = -1;
  let page;
  let qs;
  let episodeId = null;

  router('*', parseqs)
  routes.forEach(route => {
    router(
      route.path,
      (ctx, next) => {
	pagenum = getPageNum(ctx.pathname);
	qs = ctx.qs;
	// N1: Extract episodeId from path for content routes
	episodeId = getEpisodeIdFromPath(ctx.pathname);
	next();
      },
      () => {page = route.component;}
    );
  });
  router.start();
</script>

<div class="flex flex-col min-h-screen">
  <PageHeader selected={pagenum} />
  <svelte:component this={page} qs={qs} {episodeId}/>
  <PageFooter/>
</div>
