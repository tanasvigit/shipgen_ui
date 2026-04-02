import React from 'react';
import { LucideIcon } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  fullWidth?: boolean;
}

const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');

/**
 * Polished button component with consistent styling
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  loading = false,
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-600 shadow-sm',
    secondary: 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200 focus:ring-secondary-500',
    outline: 'border border-border text-secondary-700 hover:bg-secondary-50 focus:ring-secondary-500',
    ghost: 'text-secondary-700 hover:bg-secondary-100 focus:ring-secondary-500',
    danger: 'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-600 shadow-sm',
  };
  
  const sizeClasses = {
    sm: 'h-9 px-3 text-sm',
    md: 'h-10 px-4 text-sm',
    lg: 'h-11 px-5 text-base',
  };

  return (
    <button
      className={cn(baseClasses, variantClasses[variant], sizeClasses[size], fullWidth && 'w-full', className)}
      disabled={disabled || loading}
      aria-busy={loading}
      {...props}
    >
      {loading ? (
        <div className="spinner h-4 w-4" />
      ) : Icon && iconPosition === 'left' ? (
        <Icon size={size === 'sm' ? 16 : size === 'lg' ? 20 : 18} />
      ) : null}
      {children}
      {Icon && iconPosition === 'right' && !loading ? (
        <Icon size={size === 'sm' ? 16 : size === 'lg' ? 20 : 18} />
      ) : null}
    </button>
  );
};
