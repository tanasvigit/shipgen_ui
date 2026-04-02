import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  /** Rendered inline after the title (e.g. back) — stays in the fixed header row */
  titleEnd?: React.ReactNode;
  children: React.ReactNode;
  bodyScrollable?: boolean;
  bodyClassName?: string;
  showTitle?: boolean;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  titleEnd,
  children,
  bodyScrollable = true,
  bodyClassName = '',
  showTitle = true,
}) => {
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!isOpen) return;
    const id = window.requestAnimationFrame(() => {
      const root = bodyRef.current;
      if (!root) return;
      const el = root.querySelector<HTMLElement>(
        'input:not([type="hidden"]):not([disabled]), textarea:not([disabled]), select:not([disabled])',
      );
      el?.focus();
    });
    return () => window.cancelAnimationFrame(id);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div
        className="w-full max-w-3xl animate-fade-in rounded-2xl bg-white p-0 shadow-md"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title || 'Modal'}
      >
        <div className={`flex gap-3 px-6 py-4 ${showTitle ? 'items-center justify-between' : 'items-center justify-end'}`}>
          {showTitle ? (
            <div className="flex min-w-0 flex-1 items-center gap-2">
              <h2 className="truncate text-lg font-semibold text-gray-900">{title}</h2>
              {titleEnd ? <div className="flex shrink-0 items-center">{titleEnd}</div> : null}
            </div>
          ) : null}
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700"
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>
        <div
          ref={bodyRef}
          className={`max-h-[70vh] px-6 pb-5 pt-0 ${bodyScrollable ? 'overflow-y-auto' : 'overflow-hidden'} ${bodyClassName}`.trim()}
        >
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
