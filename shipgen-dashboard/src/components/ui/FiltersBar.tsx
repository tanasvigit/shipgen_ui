import React from 'react';
import Card from './Card';

interface FiltersBarProps {
  children: React.ReactNode;
  className?: string;
}

const FiltersBar: React.FC<FiltersBarProps> = ({ children, className = '' }) => {
  return (
    <Card className={className} padding="md">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 xl:grid-cols-4">{children}</div>
    </Card>
  );
};

export default FiltersBar;
