import React from 'react';
import { ChevronDown } from 'lucide-react';
import { INPUT_STYLES } from './design-tokens';
import type { CategoryKey } from './design-tokens';

interface SelectFieldProps {
  id: string;
  options: string[];
  category?: CategoryKey;
}

export const SelectField: React.FC<SelectFieldProps> = ({ id, options, category = 'neutral' }) => {
  const ringStyle = INPUT_STYLES.focusRing(category);

  return (
    <div className="relative w-full">
      <select 
        id={id} 
        defaultValue={localStorage.getItem(id) || options[0]}
        onChange={(e) => localStorage.setItem(id, e.target.value)}
        className={`${INPUT_STYLES.base} pr-10 appearance-none cursor-pointer`}
        style={ringStyle}
      >
        {options.map(opt => <option key={opt} value={opt} className="bg-[#111]">{opt}</option>)}
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-white/40">
        <ChevronDown size={16} />
      </div>
    </div>
  );
};
