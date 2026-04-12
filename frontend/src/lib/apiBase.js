/**
 * Single source of truth for API origin in the Vite SPA.
 * Prefer VITE_API_URL (matches Vite dev server proxy). VITE_BACKEND_URL is supported for legacy .env files.
 */
export function getApiBase() {
  const fromEnv =
    import.meta.env.VITE_API_URL ||
    import.meta.env.VITE_BACKEND_URL ||
    '';
  if (fromEnv) return fromEnv.replace(/\/$/, '');
  // Dev: same-origin so Vite `server.proxy` can forward /api, /assets, /swarms, etc.
  if (import.meta.env.DEV) return '';
  return 'https://api.realms2riches.com';
}

/** WebSocket origin (dev defaults to backend port 8000). */
export function getWsBase() {
  const http = getApiBase();
  if (http) return http.replace(/^https/, 'wss').replace(/^http/, 'ws');
  if (import.meta.env.DEV && typeof window !== 'undefined') {
    return `ws://${window.location.hostname}:8000`;
  }
  return 'wss://api.realms2riches.com';
}
