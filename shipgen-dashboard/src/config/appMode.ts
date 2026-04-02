// Feature flags — override via Vite env at build time (see `.env.example`).

export const APP_MODE = {
  /** In-memory mock API (no real backend). Production builds should leave this false. */
  useMockApi: import.meta.env.VITE_USE_MOCK_API === 'true',
  /** Bypass login / role checks — local demos only; never enable in public deploys. */
  disableAuth: import.meta.env.VITE_DISABLE_AUTH === 'true',
};
