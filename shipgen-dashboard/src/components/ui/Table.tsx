import React from 'react';
import { Package } from 'lucide-react';
import { TableSkeleton } from './LoadingSkeleton';
import { EmptyState } from './EmptyState';
import TablePagination from './TablePagination';

type TableAlign = 'left' | 'center' | 'right';

export interface TableColumn<T> {
  key: keyof T | string;
  title: string;
  render?: (row: T) => React.ReactNode;
  align?: TableAlign;
  isActions?: boolean;
  className?: string;
  headerClassName?: string;
}

interface TableEmptyState {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

interface TablePaginationState {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  rowKey: (row: T) => string;
  loading?: boolean;
  emptyState?: TableEmptyState;
  pagination?: TablePaginationState;
  rowClassName?: (row: T, index: number) => string;
  onRowClick?: (row: T) => void;
}

const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');
const alignClassMap: Record<TableAlign, string> = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
};

const getAlignmentClass = (align?: TableAlign, isActions?: boolean) => alignClassMap[align ?? (isActions ? 'right' : 'left')];

function Table<T>({ columns, data, rowKey, loading = false, emptyState, pagination, rowClassName, onRowClick }: TableProps<T>) {
  if (loading) {
    return (
      <div className="p-6">
        <TableSkeleton rows={5} cols={Math.max(columns.length, 5)} />
      </div>
    );
  }

  if (!data.length) {
    if (!emptyState) {
      return null;
    }

    return <EmptyState icon={Package} title={emptyState.title} description={emptyState.description} action={emptyState.action} />;
  }

  return (
    <div>
      <div className="-mx-3 overflow-x-auto px-3 sm:mx-0 sm:px-0">
        <table className="w-full min-w-[860px] table-auto lg:min-w-0">
          <thead className="border-b border-border bg-secondary-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className={cn(
                    'h-11 px-4 text-xs font-semibold uppercase tracking-wide text-secondary-600',
                    getAlignmentClass(column.align, column.isActions),
                    column.headerClassName
                  )}
                >
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {data.map((row, index) => (
              <tr
                key={rowKey(row)}
                className={cn(
                  'h-14 align-middle transition-all duration-200 hover:bg-secondary-50',
                  onRowClick && 'cursor-pointer',
                  rowClassName?.(row, index)
                )}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
              >
                {columns.map((column) => (
                  <td
                    key={String(column.key)}
                    className={cn('px-4 py-3 text-sm text-secondary-700', getAlignmentClass(column.align, column.isActions), column.className)}
                  >
                    {column.render ? column.render(row) : String((row as Record<string, unknown>)[String(column.key)] ?? '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {pagination ? (
        <TablePagination
          page={pagination.page}
          pageSize={pagination.pageSize}
          total={pagination.total}
          onPageChange={pagination.onPageChange}
        />
      ) : null}
    </div>
  );
}

export default Table;
