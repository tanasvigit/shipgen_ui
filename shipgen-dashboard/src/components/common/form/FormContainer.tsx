import React from 'react';

const cn = (...c: Array<string | false | undefined>) => c.filter(Boolean).join(' ');

export interface FormContainerProps {
  children: React.ReactNode;
  className?: string;
}

/** Soft shell: no outer border — shadow + radius define the card */
export const FormContainer: React.FC<FormContainerProps> = ({ children, className }) => (
  <div className={cn('mx-auto w-full max-w-3xl rounded-xl bg-gray-50 p-6 shadow-sm md:p-8', className)}>{children}</div>
);
