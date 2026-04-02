import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
}) => {
  const baseClasses = 'bg-gray-200 rounded';
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };
  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className}`}
      style={style}
      aria-label="Loading..."
      role="status"
    />
  );
};

export const TableSkeleton: React.FC<{ rows?: number; cols?: number }> = ({ rows = 5, cols = 5 }) => {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex space-x-4 pb-3 border-b border-gray-200">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} variant="text" width="20%" height={16} />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="flex space-x-4" style={{ animationDelay: `${rowIdx * 50}ms` }}>
          {Array.from({ length: cols }).map((_, colIdx) => (
            <Skeleton key={colIdx} variant="text" width="20%" height={20} />
          ))}
        </div>
      ))}
    </div>
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 animate-scale-in">
      <Skeleton variant="text" width="60%" height={24} className="mb-4" />
      <Skeleton variant="text" width="100%" height={16} className="mb-2" />
      <Skeleton variant="text" width="80%" height={16} />
    </div>
  );
};

export const KPISkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 animate-scale-in">
      <div className="flex items-center justify-between mb-4">
        <Skeleton variant="circular" width={48} height={48} />
        <Skeleton variant="text" width={60} height={16} />
      </div>
      <Skeleton variant="text" width="40%" height={32} className="mb-2" />
      <Skeleton variant="text" width="60%" height={16} />
    </div>
  );
};
