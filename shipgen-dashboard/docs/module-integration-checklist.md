# Module Integration Checklist

Use this checklist for every new module integration.

## 1) Service Layer

- Create `src/services/<module>Service.ts`
- Use `apiClient` only (no direct `fetch`)
- Use `normalizeList()` from `src/services/baseService.ts` for list endpoints
- Use `normalizeSingle()` for detail/create/update responses
- Add endpoint fallback via `withEndpointFallback()` only if backend has multiple route variants
- Expose standard methods:
  - `list(params)`
  - `getById(id)`
  - `create(payload)`
  - `update(id, payload)`
  - `remove(id)`

## 2) Hook Usage

- Prefer `useListWithCrud()` from `src/hooks/useListWithCrud.ts` for list + delete flows (wraps `useList`, toasts, `deleteWithConfirm`)
- Or use `useList()` alone when you do not need the shared delete helper
- Keep list fetch logic inside `useCallback`
- Return UI-ready data from service and keep components thin
- Use `reload()` after delete/update/create when list should refresh
- For consistent page chrome (search, errors, loader, empty states), use `StandardCrudListLayout` from `src/components/patterns/StandardCrudListLayout.tsx`

## 3) UI Binding

- Show loading state from `useList.loading`
- Show API errors in UI (`useList.error` + action-level error)
- Bind search/filter/sort on list state
- Ensure row actions call service methods and refresh state

## 4) CRUD Validation

- List: endpoint works with real backend
- Create: payload shape verified in UI and Postman
- Update: partial/full update works and UI refreshes
- Delete: confirm dialog + successful removal from list

## 5) Done Criteria

- No mock API path in module service
- No duplicated response normalization logic inside component
- Component uses reusable hook and reusable service helpers
- Module behavior matches vendors integration quality
