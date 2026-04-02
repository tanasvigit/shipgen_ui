import React from 'react';
import { Link } from 'react-router-dom';

interface EntityLinkProps {
  id?: string | null;
  label?: string | null;
  to: string;
  title?: string;
  className?: string;
}

const EntityLink: React.FC<EntityLinkProps> = ({ id, label, to, title, className }) => {
  const value = (id ?? '').toString().trim();
  const text = (label ?? '').toString().trim() || value;

  if (!value) {
    return <span className="text-gray-500">—</span>;
  }

  return (
    <Link
      to={`${to}/${encodeURIComponent(value)}`}
      title={title}
      className={className ?? 'text-blue-600 hover:underline cursor-pointer'}
    >
      {text}
    </Link>
  );
};

export default EntityLink;
