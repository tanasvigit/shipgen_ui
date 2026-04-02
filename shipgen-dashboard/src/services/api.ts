/**
 * Backend base URL for HTTP (axios) and socket.io.
 * Configure at build time via Vite env — see `.env.example`.
 */
function normalizeApiBase(url: string): string {
  return url.trim().replace(/\/$/, '');
}

const fromEnv = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE;

export const API_BASE_URL = normalizeApiBase(
  typeof fromEnv === 'string' && fromEnv.length > 0 ? fromEnv : 'http://127.0.0.1:8000',
);

export const API_BASE = API_BASE_URL;
