import React from 'react';

type StatusVariant = 'success' | 'pending' | 'failed' | 'info' | 'neutral';

interface StatusBadgeProps {
  label: string;
  variant?: StatusVariant;
  className?: string;
}

const variantClass: Record<StatusVariant, string> = {
  success: 'bg-success-100 text-success-700',
  pending: 'bg-warning-100 text-warning-700',
  failed: 'bg-danger-100 text-danger-700',
  info: 'bg-primary-100 text-primary-700',
  neutral: 'bg-secondary-100 text-secondary-700',
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ label, variant = 'neutral', className = '' }) => {
  return (
    <span className={`inline-flex min-h-6 items-center rounded-full px-2.5 text-xs font-medium transition-all duration-200 ${variantClass[variant]} ${className}`}>
      {label}
    </span>
  );
};

export default StatusBadge;
