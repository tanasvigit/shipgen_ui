import React from 'react';

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
  /** Skip horizontal padding (pair with module-level full-width wrapper + explicit px in className). */
  flushHorizontal?: boolean;
}

const PageContainer: React.FC<PageContainerProps> = ({ children, className = '', flushHorizontal = false }) => {
  const spacing = flushHorizontal
    ? 'space-y-5 py-3 sm:space-y-6 sm:py-4 lg:py-6'
    : 'space-y-5 p-3 sm:space-y-6 sm:p-4 lg:p-6';
  return <div className={`${spacing} ${className}`}>{children}</div>;
};

export default PageContainer;
