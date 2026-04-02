import React from 'react';
import { LucideIcon } from 'lucide-react';

interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string | null;
  helperText?: string;
  requiredMark?: boolean;
  id?: string;
  leftIcon?: LucideIcon;
  rightIcon?: LucideIcon;
}

const normalizeId = (value: string): string =>
  value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');

const InputField: React.FC<InputFieldProps> = ({
  label,
  error,
  helperText,
  requiredMark,
  className = '',
  id,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  disabled,
  ...props
}) => {
  const fallbackLabel = label ?? 'input';
  const inputId = id ?? normalizeId(fallbackLabel);
  return (
    <div className="space-y-2">
      {label ? (
        <label htmlFor={inputId} className="block text-sm font-medium text-secondary-700">
          {label} {requiredMark ? <span className="text-danger-600">*</span> : null}
        </label>
      ) : null}
      <div className="relative">
        {LeftIcon ? <LeftIcon size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-secondary-500" /> : null}
        <input
          id={inputId}
          aria-invalid={Boolean(error)}
          disabled={disabled}
          className={cn(
            'w-full rounded-md border border-border bg-white px-3 text-sm text-neutral-900 transition-all duration-200 placeholder:text-secondary-500 focus:border-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-100 disabled:cursor-not-allowed disabled:bg-secondary-50 disabled:text-secondary-500',
            LeftIcon && 'pl-9',
            RightIcon && 'pr-9',
            error && 'border-danger-600 focus:border-danger-600 focus:ring-danger-100',
            'h-10',
            className
          )}
          {...props}
        />
        {RightIcon ? <RightIcon size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-secondary-500" /> : null}
      </div>
      {error ? (
        <p className="text-xs text-danger-600">{error}</p>
      ) : helperText ? (
        <p className="text-xs text-secondary-500">{helperText}</p>
      ) : null}
    </div>
  );
};

export default InputField;
