/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  /** @deprecated Prefer VITE_API_BASE_URL — kept for older `.env` files */
  readonly VITE_API_BASE?: string;
  readonly VITE_USE_MOCK_API?: string;
  readonly VITE_DISABLE_AUTH?: string;
  readonly VITE_DEV_AUTH?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
