import { useCallback, useState, type DependencyList } from 'react';
import useList from './useList';
import { getApiErrorMessage } from '../services/apiErrors';
import { useToast } from '../components/ui/ToastProvider';

export interface DeleteWithConfirmOptions {
  confirmMessage: string;
  successMessage?: string;
  errorFallback?: string;
}

/**
 * useList + action error state + confirm/delete/reload + success toast.
 * Use with apiClient-backed services for consistent list CRUD UX.
 */
export function useListWithCrud<T>(loader: () => Promise<T[]>, deps: DependencyList = []) {
  const { showToast } = useToast();
  const { data, loading, error, reload, setData, setError } = useList<T>(loader, deps);
  const [actionError, setActionError] = useState<string | null>(null);

  const deleteWithConfirm = useCallback(
    async (id: string, remove: (rid: string) => Promise<void>, opts: DeleteWithConfirmOptions) => {
      if (!window.confirm(opts.confirmMessage)) return;
      try {
        setActionError(null);
        await remove(id);
        await reload();
        showToast(opts.successMessage ?? 'Deleted', 'success');
      } catch (e: unknown) {
        setActionError(getApiErrorMessage(e, opts.errorFallback ?? 'Delete failed'));
      }
    },
    [reload, showToast]
  );

  return {
    rows: data,
    loading,
    error,
    actionError,
    setActionError,
    reload,
    setData,
    setError,
    deleteWithConfirm,
  };
}

export default useListWithCrud;
