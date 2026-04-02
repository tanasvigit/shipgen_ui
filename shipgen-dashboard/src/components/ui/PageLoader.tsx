import React from 'react';

export interface PageLoaderProps {
  /** Tailwind min-height class, e.g. h-64 */
  minHeightClass?: string;
  className?: string;
}

/**
 * Standard full-width loading indicator for pages and panels.
 */
export const PageLoader: React.FC<PageLoaderProps> = ({
  minHeightClass = 'min-h-[16rem]',
  className = '',
}) => (
  <div
    className={`flex items-center justify-center ${minHeightClass} ${className}`}
    role="status"
    aria-live="polite"
    aria-busy="true"
  >
    <span className="sr-only">Loading</span>
    <div className="h-9 w-9 animate-spin rounded-full border-2 border-primary-200 border-t-primary-600" />
  </div>
);

export default PageLoader;
