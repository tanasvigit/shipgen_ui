import React from 'react';

interface FormMessageProps {
  error?: string | null;
  hint?: string;
}

const FormMessage: React.FC<FormMessageProps> = ({ error, hint }) => {
  if (error) {
    return <p className="mt-1 text-xs text-danger-600">{error}</p>;
  }
  if (hint) {
    return <p className="mt-1 text-xs text-gray-500">{hint}</p>;
  }
  return null;
};

export default FormMessage;
