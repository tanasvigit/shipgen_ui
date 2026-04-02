import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Plus, Search, type LucideIcon } from 'lucide-react';
import { PageLoader } from '../ui/PageLoader';
import { EmptyState } from '../ui/EmptyState';

export interface StandardCrudListLayoutProps {
  title: string;
  subtitle: string;
  /** Omit both to hide the primary action button (read-only lists). */
  createHref?: string;
  createOnClick?: () => void;
  createLabel?: string;
  /** Optional filters (e.g. status dropdown) rendered below search. */
  filters?: React.ReactNode;
  searchPlaceholder: string;
  searchTerm: string;
  onSearchChange: (value: string) => void;
  error: string | null;
  actionError: string | null;
  loading: boolean;
  rowCount: number;
  filteredCount: number;
  emptyIcon: LucideIcon;
  emptyTitleNoData: string;
  emptyTitleNoMatch: string;
  emptyDescriptionNoData: string;
  emptyDescriptionNoMatch: string;
  emptyAction?: React.ReactNode;
  noMatchAction?: React.ReactNode;
  failedLoadTitle?: string;
  failedLoadDescription?: string;
  /** Table or other primary content when rows exist */
  children: React.ReactNode;
}

/**
 * Shared layout for module list pages: alerts, search, loader, empty states, bordered card shell.
 */
export const StandardCrudListLayout: React.FC<StandardCrudListLayoutProps> = ({
  title,
  subtitle,
  createHref,
  createOnClick,
  createLabel,
  filters,
  searchPlaceholder,
  searchTerm,
  onSearchChange,
  error,
  actionError,
  loading,
  rowCount,
  filteredCount,
  emptyIcon: EmptyIcon,
  emptyTitleNoData,
  emptyTitleNoMatch,
  emptyDescriptionNoData,
  emptyDescriptionNoMatch,
  emptyAction,
  noMatchAction,
  failedLoadTitle = 'Could not load data',
  failedLoadDescription = 'Check the message above or try again.',
  children,
}) => {
  return (
    <div className="space-y-5 sm:space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-xl font-bold text-gray-900 sm:text-2xl">{title}</h1>
          <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
        </div>
        {createLabel ? (
          createOnClick ? (
            <button
              type="button"
              onClick={createOnClick}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 sm:w-auto"
            >
              <Plus size={16} />
              <span>{createLabel}</span>
            </button>
          ) : createHref ? (
            <Link
              to={createHref}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 sm:w-auto"
            >
              <Plus size={16} />
              <span>{createLabel}</span>
            </Link>
          ) : null
        ) : null}
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 size-[18px] -translate-y-1/2 text-gray-400" />
        <input
          type="search"
          placeholder={searchPlaceholder}
          aria-label={searchPlaceholder}
          autoComplete="off"
          className="w-full rounded-lg border border-gray-200 bg-white py-2 pl-10 pr-4 outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {filters}

      {(error || actionError) && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700">
          <AlertCircle size={18} />
          <span>{actionError || error}</span>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
        {loading ? (
          <PageLoader minHeightClass="min-h-[16rem]" />
        ) : error && rowCount === 0 ? (
          <EmptyState
            icon={EmptyIcon}
            title={failedLoadTitle}
            description={failedLoadDescription}
          />
        ) : filteredCount === 0 ? (
          <EmptyState
            icon={EmptyIcon}
            title={rowCount === 0 ? emptyTitleNoData : emptyTitleNoMatch}
            description={rowCount === 0 ? emptyDescriptionNoData : emptyDescriptionNoMatch}
            action={rowCount === 0 ? emptyAction : noMatchAction}
          />
        ) : (
          children
        )}
      </div>
    </div>
  );
};
