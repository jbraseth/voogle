import Home from './lib/pages/Home.svelte'
import Content from './lib/pages/Content.svelte'
import Query from './lib/pages/Query.svelte'
import About from './lib/pages/About.svelte'
import Courses from './routes/Courses.svelte'
import CourseDetail from './routes/CourseDetail.svelte'
import Session from './routes/Session.svelte'

export const routes = [
  {path: "/", component: Home},
  {path: "/query", component: Query},
  {path: "/about", component: About},
  {path: "/content", component: Content},
  {path: "/content/:episodeId", component: Content},
  {path: "/courses", component: Courses},
  {path: "/courses/:slug", component: CourseDetail},
  {path: "/session/:course/:sessionId", component: Session},
];

const routeMap = {
  "/": -1, "/query": 0, "/about": 1, "/content": 3
}

// N1: Extract episodeId from path for /content/:episodeId route
export function getEpisodeIdFromPath(path) {
  const match = path.match(/^\/content\/([^/?]+)/);
  return match ? match[1] : null;
}

// N2: Extract slug from path for /courses/:slug route
export function getSlugFromPath(path) {
  const match = path.match(/^\/courses\/([^/?]+)$/);
  return match ? match[1] : null;
}

// N2: Extract course and sessionId from path for /session/:course/:sessionId route
export function getSessionParamsFromPath(path) {
  const match = path.match(/^\/session\/([^/?]+)\/([^/?]+)/);
  return match ? { course: match[1], sessionId: match[2] } : null;
}

export function getPageNum(path) {
  return routeMap[path]
}

export function parseqs(ctx, next) {
  ctx.qs = new URLSearchParams(ctx.querystring);
  next();
}
