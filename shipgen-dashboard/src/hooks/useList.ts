import { DependencyList, useCallback, useEffect, useState } from 'react';
import { getApiErrorMessage } from '../services/apiErrors';

export const useList = <T>(
  loader: () => Promise<T[]>,
  deps: DependencyList = []
) => {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const rows = await loader();
      setData(rows);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Failed to load data'));
    } finally {
      setLoading(false);
    }
  }, [loader]);

  useEffect(() => {
    void reload();
  }, [reload, ...deps]);

  return {
    data,
    setData,
    loading,
    error,
    setError,
    reload,
  };
};

export default useList;
