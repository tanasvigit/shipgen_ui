import React from 'react';

interface AppTableProps {
  children: React.ReactNode;
  className?: string;
}

const AppTable: React.FC<AppTableProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-soft overflow-hidden ${className}`}>
      <div className="-mx-3 overflow-x-auto px-3 sm:mx-0 sm:px-0">{children}</div>
    </div>
  );
};

export default AppTable;
