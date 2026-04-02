import React from 'react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
}

const SelectField: React.FC<SelectFieldProps> = ({ label, id, options, className = '', ...props }) => {
  return (
    <div className="space-y-2">
      {label ? (
        <label htmlFor={id} className="block text-sm font-medium text-secondary-700">
          {label}
        </label>
      ) : null}
      <select
        id={id}
        className={`h-10 w-full rounded-md border border-border bg-white px-3 text-sm text-neutral-900 transition-all duration-200 focus:border-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-100 ${className}`}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SelectField;
