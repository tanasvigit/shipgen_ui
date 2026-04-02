import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');

const paddingClasses: Record<NonNullable<CardProps['padding']>, string> = {
  none: '',
  sm: 'p-4',
  md: 'p-5',
  lg: 'p-6',
};

const Card: React.FC<CardProps> = ({ children, className, padding = 'md' }) => {
  return (
    <section
      className={cn(
        'rounded-lg border border-border bg-white shadow-card-soft transition-all duration-200 hover:shadow-soft',
        paddingClasses[padding],
        className
      )}
    >
      {children}
    </section>
  );
};

export default Card;
