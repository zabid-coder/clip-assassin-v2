import React, { useState, useRef, useEffect } from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { BUTTON_VARIANTS, CATEGORY_COLORS } from './design-tokens';
import type { CategoryKey } from './design-tokens';

interface ActionButtonProps {
  onClick: () => void | Promise<void>;
  text: string;
  category?: CategoryKey;
  variant?: 'primary' | 'secondary';
  colorClass?: string; // keeping for backward compatibility in parts not yet refactored
  isLoading?: boolean;
  disabled?: boolean;
  title?: string;
  requiresConfirm?: boolean;
}

export const ActionButton: React.FC<ActionButtonProps> = ({ 
  onClick, 
  text, 
  category = 'neutral',
  variant = 'primary',
  colorClass,
  isLoading = false,
  disabled = false,
  title,
  requiresConfirm = false
}) => {
  const [internalStatus, setInternalStatus] = useState<'idle' | 'confirming' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleClick = async () => {
    if (disabled || isLoading || internalStatus === 'loading') return;

    if (requiresConfirm && internalStatus === 'idle') {
      setInternalStatus('confirming');
      timeoutRef.current = setTimeout(() => {
        setInternalStatus('idle');
      }, 3000);
      return;
    }

    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    
    // Proceed to execute
    setInternalStatus('loading');
    setErrorMessage(null);

    try {
      await onClick();
      setInternalStatus('success');
      setTimeout(() => setInternalStatus('idle'), 2000);
    } catch (err: any) {
      setInternalStatus('error');
      setErrorMessage(err.message || 'Action failed');
      setTimeout(() => setInternalStatus('idle'), 3000);
    }
  };

  const isActuallyLoading = isLoading || internalStatus === 'loading';
  const isDisabled = disabled || isActuallyLoading;

  // Use token styles if colorClass is not provided
  let btnClass = colorClass || "";
  let btnStyle: React.CSSProperties = {};

  if (!colorClass) {
    const variantStyles = variant === 'primary' ? BUTTON_VARIANTS.primary(category) : BUTTON_VARIANTS.secondary;
    btnClass = variantStyles.className;
    btnStyle = variantStyles.style;
  } else {
    btnClass = `py-3 rounded-xl text-sm font-semibold shadow-lg hover:shadow-xl transition-all duration-300 ease-out hover:-translate-y-0.5 hover:brightness-110 active:scale-95 active:translate-y-0 flex items-center justify-center gap-2 ${colorClass}`;
  }

  // Override styles for specific states
  if (internalStatus === 'confirming') {
    btnClass = 'py-3 rounded-xl text-sm font-semibold shadow-lg transition-all duration-300 ease-out flex items-center justify-center gap-2 bg-rose-500 text-white animate-pulse';
    btnStyle = { boxShadow: `0 0 24px rgba(244, 63, 94, 0.4)` };
  } else if (internalStatus === 'success') {
    btnClass = 'py-3 rounded-xl text-sm font-semibold shadow-lg transition-all duration-300 ease-out flex items-center justify-center gap-2 text-[#0A0F0D]';
    // Flash the category color brightly
    btnStyle = { backgroundColor: CATEGORY_COLORS[category].text, boxShadow: `0 0 30px ${CATEGORY_COLORS[category].solid}` };
  } else if (internalStatus === 'error') {
    btnClass = 'py-3 rounded-xl text-sm font-semibold shadow-lg transition-all duration-300 ease-out flex items-center justify-center gap-2 bg-red-600 text-white';
    btnStyle = { boxShadow: `0 0 24px rgba(220, 38, 38, 0.5)` };
  }

  let displayText = text;
  if (internalStatus === 'confirming') displayText = 'Click again to confirm';
  else if (internalStatus === 'loading' || isLoading) displayText = 'Processing...';
  else if (internalStatus === 'success') displayText = 'Success!';
  else if (internalStatus === 'error') displayText = errorMessage || 'Failed';

  return (
    <button 
      onClick={handleClick}
      disabled={isDisabled}
      title={title}
      className={`w-full flex items-center justify-center gap-2 ${btnClass} ${(disabled && internalStatus === 'idle') ? 'opacity-50 cursor-not-allowed hover:-translate-y-0 hover:shadow-lg active:scale-100 hover:brightness-100' : ''}`}
      style={btnStyle}
    >
      {isActuallyLoading && <Loader2 size={14} className="animate-spin" />}
      {internalStatus === 'success' && <CheckCircle2 size={16} />}
      {internalStatus === 'error' && <AlertCircle size={16} />}
      {displayText}
    </button>
  );
};
