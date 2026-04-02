type UnknownRecord = Record<string, unknown>;

const DEFAULT_LIST_KEYS = ['data', 'items', 'results'] as const;
const DEFAULT_SINGLE_KEYS = ['data', 'item', 'result'] as const;

export const normalizeList = <T>(
  response: unknown,
  additionalKeys: string[] = []
): T[] => {
  if (Array.isArray(response)) return response as T[];
  if (!response || typeof response !== 'object') return [];

  const source = response as UnknownRecord;
  const keys = [...DEFAULT_LIST_KEYS, ...additionalKeys];

  for (const key of keys) {
    const value = source[key];
    if (Array.isArray(value)) return value as T[];
  }

  return [];
};

export const normalizeSingle = <T>(
  response: unknown,
  additionalKeys: string[] = []
): T | null => {
  if (!response || typeof response !== 'object') return null;

  const source = response as UnknownRecord;
  const keys = [...DEFAULT_SINGLE_KEYS, ...additionalKeys];

  for (const key of keys) {
    const value = source[key];
    if (value && typeof value === 'object') return value as T;
  }

  return source as T;
};

export const withEndpointFallback = async <T>(
  endpoints: string[],
  request: (endpoint: string) => Promise<T>
): Promise<T> => {
  if (!endpoints.length) {
    throw new Error('No API endpoints configured');
  }

  let lastError: unknown;
  for (const endpoint of endpoints) {
    try {
      return await request(endpoint);
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError instanceof Error ? lastError : new Error('Request failed');
};
