import React from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, description, action }) => {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="min-w-0">
        <h1 className="text-xl font-semibold text-neutral-900 sm:text-2xl">{title}</h1>
        {description ? <p className="mt-1 text-sm text-secondary-600">{description}</p> : null}
      </div>
      {action ? <div className="w-full sm:w-auto">{action}</div> : null}
    </div>
  );
};

export default PageHeader;
