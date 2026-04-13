import React from 'react';
import { Calendar } from 'lucide-react';

const cn = (...c: Array<string | false | undefined>) => c.filter(Boolean).join(' ');

const inputStyles =
  'w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-sm transition placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:opacity-70';

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, type, ...props },
  ref,
) {
  const innerRef = React.useRef<HTMLInputElement | null>(null);
  const isDateLike = type === 'date' || type === 'datetime-local';

  const setRefs = (el: HTMLInputElement | null) => {
    innerRef.current = el;
    if (typeof ref === 'function') ref(el);
    else if (ref) ref.current = el;
  };

  const openPicker = () => {
    const el = innerRef.current;
    if (!el) return;
    if (typeof el.showPicker === 'function') el.showPicker();
    else el.focus();
  };

  if (!isDateLike) {
    return <input ref={setRefs} type={type} className={cn(inputStyles, className)} {...props} />;
  }

  return (
    <div className="relative">
      <button
        type="button"
        aria-label="Open date picker"
        title="Open date picker"
        onClick={openPicker}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
      >
        <Calendar size={14} />
      </button>
      <input
        ref={setRefs}
        type={type}
        className={cn(
          inputStyles,
          'pl-9 [&&::-webkit-calendar-picker-indicator]:opacity-0 [&&::-webkit-calendar-picker-indicator]:w-0',
          className,
        )}
        {...props}
      />
    </div>
  );
});
