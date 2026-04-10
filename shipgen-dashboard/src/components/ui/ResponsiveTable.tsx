import React from 'react';

interface Column<T> {
  key: string;
  header: string;
  render: (item: T) => React.ReactNode;
  mobileHidden?: boolean;
  sticky?: boolean;
  align?: 'left' | 'right' | 'center';
}

interface ResponsiveTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  className?: string;
}

/**
 * Responsive table that converts to card layout on mobile
 */
export function ResponsiveTable<T>({
  data,
  columns,
  keyExtractor,
  onRowClick,
  emptyMessage = 'No data available',
  className = '',
}: ResponsiveTableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <>
      {/* Desktop Table */}
      <div className={`hidden md:block overflow-x-auto ${className}`}>
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`py-3 px-4 text-xs font-semibold text-gray-600 uppercase ${
                    col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
                  } ${
                    col.sticky ? 'sticky left-0 bg-gray-50 z-10' : ''
                  }`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map((item, idx) => (
              <tr
                key={keyExtractor(item)}
                onClick={() => onRowClick?.(item)}
                className={`table-row table-row-zebra ${
                  onRowClick ? 'cursor-pointer' : ''
                }`}
                style={{ animationDelay: `${idx * 40}ms` }}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={`py-3 px-4 ${
                      col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
                    } ${
                      col.sticky ? 'sticky left-0 bg-white z-10' : ''
                    }`}
                  >
                    {col.render(item)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card Layout */}
      <div className="md:hidden space-y-4">
        {data.map((item, idx) => (
          <div
            key={keyExtractor(item)}
            onClick={() => onRowClick?.(item)}
            className={`bg-white rounded-xl border border-gray-200 p-4 ${
              onRowClick ? 'cursor-pointer hover:border-blue-300 transition-colors' : ''
            } animate-scale-in`}
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            {columns
              .filter((col) => !col.mobileHidden)
              .map((col) => (
                <div key={col.key} className="mb-3 last:mb-0">
                  <div className="text-xs font-medium text-gray-500 uppercase mb-1">
                    {col.header}
                  </div>
                  <div className="text-sm text-gray-900">{col.render(item)}</div>
                </div>
              ))}
          </div>
        ))}
      </div>
    </>
  );
}
