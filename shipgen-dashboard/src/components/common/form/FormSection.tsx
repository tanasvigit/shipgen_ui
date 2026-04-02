import React from 'react';

const cn = (...c: Array<string | false | undefined>) => c.filter(Boolean).join(' ');

export interface FormSectionProps {
  children: React.ReactNode;
  className?: string;
}

/** Responsive 2-column field grid; use `md:col-span-2` on FormField for full-width rows */
export const FormSection: React.FC<FormSectionProps> = ({ children, className }) => (
  <div className={cn('grid grid-cols-1 gap-5 md:grid-cols-2', className)}>{children}</div>
);
