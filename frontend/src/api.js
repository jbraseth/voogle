// Use nullish coalescing - empty string is valid (means use relative URL)
const BASE = import.meta.env.VITE_API_HOST ?? ''
const PORT = import.meta.env.VITE_API_PORT ?? ''
const PREFIX = import.meta.env.VITE_API_PREFIX ?? ''

// Build API URL - supports relative URLs (empty BASE) for dev proxy
function buildApiUrl() {
  if (!BASE) {
    // Relative URL - use prefix only (e.g., "/api")
    return PREFIX || '/api';
  }
  const isDefaultPort =
    (BASE.startsWith('http://') && PORT === '80') ||
    (BASE.startsWith('https://') && PORT === '443');

  if (!PORT || isDefaultPort) {
    return BASE + PREFIX;
  }
  return BASE + ':' + PORT + PREFIX;
}

export const API_URL = buildApiUrl();
