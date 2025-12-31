// Use nullish coalescing - empty string is valid (means use relative URL)
const BASE = import.meta.env.VITE_API_HOST ?? ''
const PORT = import.meta.env.VITE_API_PORT ?? ''
const PREFIX = import.meta.env.VITE_API_PREFIX ?? ''

function isDefaultPort(base, port) {
  return (base.startsWith('http://') && port === '80') ||
         (base.startsWith('https://') && port === '443');
}

// Build API origin (host:port only, no prefix) for local media URL rewriting
function buildApiOrigin() {
  if (!BASE) {
    return '';
  }
  if (!PORT || isDefaultPort(BASE, PORT)) {
    return BASE;
  }
  return BASE + ':' + PORT;
}

// Build full API URL with prefix
function buildApiUrl() {
  if (!BASE) {
    return PREFIX || '/api';
  }
  return buildApiOrigin() + PREFIX;
}

export const API_ORIGIN = buildApiOrigin();
export const API_URL = buildApiUrl();
