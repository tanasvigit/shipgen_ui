import React from 'react';

const cn = (...c: Array<string | false | undefined>) => c.filter(Boolean).join(' ');

export interface FormActionsProps {
  onCancel: () => void;
  cancelLabel?: string;
  submitLabel: string;
  saving?: boolean;
  submitDisabled?: boolean;
  className?: string;
  showSubmit?: boolean;
}

export const FormActions: React.FC<FormActionsProps> = ({
  onCancel,
  cancelLabel = 'Cancel',
  submitLabel,
  saving = false,
  submitDisabled = false,
  className,
  showSubmit = true,
}) => (
  <div className={cn('mt-6 flex flex-wrap items-center justify-center gap-3', className)}>
    <button
      type="button"
      onClick={onCancel}
      className="rounded-full border border-gray-200 bg-white px-6 py-2.5 text-sm font-medium text-gray-600 transition hover:bg-gray-50"
    >
      {cancelLabel}
    </button>
    {showSubmit ? (
      <button
        type="submit"
        disabled={saving || submitDisabled}
        className="rounded-full bg-blue-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {saving ? 'Saving...' : submitLabel}
      </button>
    ) : null}
  </div>
);
