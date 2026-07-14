import React, { useState } from 'react';
import { Info, Pin } from 'lucide-react';
import { CARD_STYLES, SPACING } from './design-tokens';
import type { CategoryKey } from './design-tokens';

const TooltipHelp = ({ text }: { text: string }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="relative inline-block ml-2 mt-0.5">
      <button 
        onMouseEnter={() => setShow(true)} 
        onMouseLeave={() => setShow(false)}
        onClick={() => setShow(!show)}
        className="text-white/30 hover:text-white/70 transition-colors focus:outline-none"
      >
        <Info size={14} />
      </button>
      {show && (
        <div className="absolute z-50 left-6 -top-2 w-64 p-3 bg-[#111]/95 backdrop-blur-xl border border-white/10 rounded-xl text-xs text-white/90 shadow-2xl leading-relaxed font-normal">
          {text}
        </div>
      )}
    </div>
  );
};

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  category?: CategoryKey;
  description?: string; // New inline description
  warning?: string; // New destructive warning
  helpText?: string;
  children: React.ReactNode;
  className?: string;
  id?: string;
  isFavorite?: boolean;
  onToggleFavorite?: () => void;
  hidden?: boolean;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({ 
  icon, title, category = 'neutral', description, warning, helpText, children, className = "", 
  id, isFavorite, onToggleFavorite, hidden = false
}) => {
  if (hidden) return null;

  const iconStyle = CARD_STYLES.iconWrapper(category);

  return (
  <div className={`${CARD_STYLES.base} ${CARD_STYLES.minHeight} ${className}`}>
    
    {id && onToggleFavorite && (
      <button 
        onClick={onToggleFavorite}
        className={`absolute top-4 right-4 p-2 rounded-full transition-all duration-300 ${isFavorite ? 'bg-white/10 opacity-100' : 'text-white/20 hover:text-white/60 hover:bg-white/5 opacity-0 group-hover:opacity-100'}`}
        style={isFavorite ? { color: iconStyle.style.color } : {}}
        title={isFavorite ? "Unpin from Dashboard" : "Pin to Dashboard"}
      >
        <Pin size={14} className={isFavorite ? "fill-current" : ""} />
      </button>
    )}

    <div className="flex items-start gap-3 mb-5 shrink-0 pr-8">
      <div className={iconStyle.className} style={iconStyle.style}>
        {icon}
      </div>
      <div className="flex flex-col">
        <div className="flex items-center">
          <h3 className="font-semibold text-lg text-white/90 leading-tight">{title}</h3>
          {helpText && <TooltipHelp text={helpText} />}
        </div>
        {description && <p className="text-xs text-white/50 mt-1 leading-snug">{description}</p>}
      </div>
    </div>
    
    <div className={`mt-auto flex flex-col ${SPACING.cardInternalStack}`}>
      {children}
      {warning && <p className="text-[10px] text-rose-400/80 mt-2">⚠ {warning}</p>}
    </div>
  </div>
  );
};
