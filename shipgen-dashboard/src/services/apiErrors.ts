import axios from 'axios';

const DEFAULT_FALLBACK = 'Something went wrong. Please try again.';

const STATUS_MESSAGES: Record<number, string> = {
  400: 'Invalid request. Check your input and try again.',
  401: 'Session expired. Please sign in again.',
  403: "You don't have permission to do that.",
  404: 'We could not find what you were looking for.',
  409: 'This action conflicts with the current state.',
  422: 'Some fields are invalid. Check the form and try again.',
  429: 'Too many requests. Please wait a moment.',
  500: 'Something went wrong on our side. Please try again later.',
  502: 'Service temporarily unavailable. Please try again.',
  503: 'Service temporarily unavailable. Please try again.',
};

const detailToString = (detail: unknown): string | null => {
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (!Array.isArray(detail)) return null;
  const parts = detail
    .map((item) => {
      if (item && typeof item === 'object' && 'msg' in item) {
        const msg = (item as { msg: unknown }).msg;
        return typeof msg === 'string' ? msg : null;
      }
      if (typeof item === 'string') return item;
      return null;
    })
    .filter((x): x is string => Boolean(x));
  return parts.length ? parts.join(' ') : null;
};

/**
 * Maps Axios / FastAPI errors to a single user-facing string.
 */
export function getApiErrorMessage(error: unknown, fallback: string = DEFAULT_FALLBACK): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data;

    if (data && typeof data === 'object') {
      const rec = data as Record<string, unknown>;
      const fromDetail = detailToString(rec.detail);
      if (fromDetail) return fromDetail;
      const msg = rec.message;
      if (typeof msg === 'string' && msg.trim()) return msg;
    }

    if (status != null && STATUS_MESSAGES[status]) {
      return STATUS_MESSAGES[status];
    }

    if (error.message === 'Network Error') {
      return 'Network error. Check your connection and try again.';
    }

    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please try again.';
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
}
