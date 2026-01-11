import Home from './lib/pages/Home.svelte'
import Content from './lib/pages/Content.svelte'
import Query from './lib/pages/Query.svelte'
import About from './lib/pages/About.svelte'

export const routes = [
  {path: "/", component: Home},
  {path: "/query", component: Query},
  {path: "/about", component: About},
  {path: "/content", component: Content},
  {path: "/content/:episodeId", component: Content},
];

const routeMap = {
  "/": -1, "/query": 0, "/about": 1, "/content": 3
}

// N1: Extract episodeId from path for /content/:episodeId route
export function getEpisodeIdFromPath(path) {
  const match = path.match(/^\/content\/([^/?]+)/);
  return match ? match[1] : null;
}

export function getPageNum(path) {
  return routeMap[path]
}

export function parseqs(ctx, next) {
  ctx.qs = new URLSearchParams(ctx.querystring);
  next();
}
