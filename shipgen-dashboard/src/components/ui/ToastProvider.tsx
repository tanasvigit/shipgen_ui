import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

const typeClass: Record<ToastType, string> = {
  success: 'bg-success-50 border-success-100 text-success-700',
  error: 'bg-danger-50 border-danger-100 text-danger-700',
  info: 'bg-primary-50 border-primary-100 text-primary-700',
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [items, setItems] = useState<ToastItem[]>([]);

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    setItems((prev) => [...prev, { id, message, type }]);
    window.setTimeout(() => {
      setItems((prev) => prev.filter((x) => x.id !== id));
    }, 2500);
  }, []);

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 z-[100] space-y-2 w-[320px] max-w-[calc(100vw-2rem)]">
        {items.map((item) => (
          <div key={item.id} className={`border rounded-lg px-3 py-2 text-sm shadow-soft transition-all duration-200 ${typeClass[item.type]}`}>
            {item.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextType => {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    return { showToast: () => undefined };
  }
  return ctx;
};

