/**
 * Shared API response shapes for services and apiClient typing.
 */

export interface PaginationMeta {
  total: number;
  page: number;
  pageSize: number;
}

/** Standard paginated list result returned by services after mapping to UI models. */
export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

/**
 * Common JSON shapes for list endpoints before {@link normalizeList}.
 * Backend may return a bare array or a keyed collection.
 */
export type ListResponse<T> =
  | T[]
  | {
      data?: T[];
      items?: T[];
      results?: T[];
    }
  | Record<string, unknown>;
