import React from 'react';

const cn = (...c: Array<string | false | undefined>) => c.filter(Boolean).join(' ');

export interface FormFieldProps {
  label: React.ReactNode;
  required?: boolean;
  children: React.ReactNode;
  error?: string | null;
  htmlFor?: string;
  className?: string;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  required,
  children,
  error,
  htmlFor,
  className,
}) => (
  <div className={cn(className)}>
    <label htmlFor={htmlFor} className="mb-1 block text-sm font-medium text-gray-700">
      {label}
      {required ? (
        <span className="ml-1 text-red-500" aria-hidden>
          *
        </span>
      ) : null}
    </label>
    {children}
    {error ? <p className="mt-1 text-xs text-red-500">{error}</p> : null}
  </div>
);
