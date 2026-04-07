import React, { useCallback, useEffect, useRef, useState } from 'react';
import { ChevronDown, Loader2, User } from 'lucide-react';
import { customersService } from '../../services/customersService';
import type { UiCustomer } from '../../services/customersService';

export interface CustomerSelectorProps {
  value: string;
  onChange: (customerUuid: string, displayName: string) => void;
  /** Shown when the parent already knows the label (e.g. order load). */
  initialLabel?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string | null;
  id?: string;
}

const CustomerSelector: React.FC<CustomerSelectorProps> = ({
  value,
  onChange,
  initialLabel = '',
  disabled = false,
  required = false,
  error = null,
  id = 'customer-selector',
}) => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [options, setOptions] = useState<UiCustomer[]>([]);
  const [loading, setLoading] = useState(false);
  const [label, setLabel] = useState(initialLabel);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLabel(initialLabel);
  }, [initialLabel]);

  useEffect(() => {
    if (!value) return;
    if (initialLabel?.trim()) return;
    let cancelled = false;
    void (async () => {
      try {
        const c = await customersService.getById(value);
        if (!cancelled) setLabel(c.name ?? '');
      } catch {
        if (!cancelled) setLabel('');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [value, initialLabel]);

  const fetchOptions = useCallback(async (search: string) => {
    setLoading(true);
    try {
      const res = await customersService.list({
        page: 1,
        pageSize: 40,
        search: search.trim() || undefined,
      });
      setOptions(res.data);
    } catch {
      setOptions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!open) return;
    const t = window.setTimeout(() => {
      void fetchOptions(query);
    }, 280);
    return () => window.clearTimeout(t);
  }, [open, query, fetchOptions]);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  const select = (c: UiCustomer) => {
    const uuid = c.uuid ?? '';
    const name = c.name ?? '';
    setLabel(name);
    onChange(uuid, name);
    setOpen(false);
    setQuery('');
  };

  const display = label || (value ? 'Loading…' : '');

  return (
    <div ref={wrapRef} className="relative md:col-span-2">
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-gray-700">
        Customer {required ? <span className="text-red-500">*</span> : null}
      </label>
      <button
        type="button"
        id={id}
        disabled={disabled}
        onClick={() => !disabled && setOpen((o) => !o)}
        className={`flex w-full items-center justify-between rounded-lg border bg-white px-3 py-2 text-left text-sm outline-none transition focus:ring-2 focus:ring-blue-500 ${
          error ? 'border-red-300' : 'border-gray-200'
        } ${disabled ? 'cursor-not-allowed opacity-60' : 'hover:border-gray-300'}`}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <span className="flex min-w-0 items-center gap-2">
          <User size={16} className="flex-shrink-0 text-gray-400" />
          <span className="truncate text-gray-900">{display || 'Search and select a customer…'}</span>
        </span>
        <ChevronDown size={18} className="flex-shrink-0 text-gray-400" />
      </button>
      {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : null}

      {open ? (
        <div className="absolute z-50 mt-1 w-full rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
          <div className="border-b border-gray-100 px-2 pb-2 pt-1">
            <input
              type="search"
              autoFocus
              placeholder="Search name or phone…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full rounded-md border border-gray-200 px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Search customers"
            />
          </div>
          <ul className="max-h-56 overflow-y-auto py-1" role="listbox">
            {loading ? (
              <li className="flex items-center justify-center gap-2 px-3 py-4 text-sm text-gray-500">
                <Loader2 size={16} className="animate-spin" />
                Loading…
              </li>
            ) : options.length === 0 ? (
              <li className="px-3 py-3 text-center text-sm text-gray-500">No customers match.</li>
            ) : (
              options.map((c) => {
                const uuid = c.uuid ?? '';
                return (
                  <li key={uuid || c.public_id || String(c.id)}>
                    <button
                      type="button"
                      role="option"
                      className="w-full px-3 py-2 text-left text-sm hover:bg-blue-50"
                      onClick={() => select(c)}
                    >
                      <span className="font-medium text-gray-900">{c.name ?? '—'}</span>
                      {c.phone ? <span className="mt-0.5 block text-xs text-gray-500">{c.phone}</span> : null}
                    </button>
                  </li>
                );
              })
            )}
          </ul>
        </div>
      ) : null}
    </div>
  );
};

export default CustomerSelector;
