import React from 'react';

const cn = (...c: Array<string | false | undefined>) => c.filter(Boolean).join(' ');

const selectChevron =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")";

const selectStyles =
  'w-full appearance-none rounded-lg border border-gray-200 bg-white bg-[length:1rem] bg-[center_right_0.75rem] bg-no-repeat px-3 py-2.5 pr-10 text-sm text-gray-900 shadow-sm transition focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:opacity-70';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  placeholder?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { className, placeholder, children, style, ...props },
  ref,
) {
  return (
    <select
      ref={ref}
      className={cn(selectStyles, className)}
      style={{ backgroundImage: selectChevron, ...style }}
      {...props}
    >
      {placeholder != null && placeholder !== '' ? (
        <option value="" disabled>
          {placeholder}
        </option>
      ) : null}
      {children}
    </select>
  );
});
