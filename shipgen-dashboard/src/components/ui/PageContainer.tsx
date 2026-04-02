import React from 'react';

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

const PageContainer: React.FC<PageContainerProps> = ({ children, className = '' }) => {
  return <div className={`space-y-5 p-3 sm:space-y-6 sm:p-4 lg:p-6 ${className}`}>{children}</div>;
};

export default PageContainer;
