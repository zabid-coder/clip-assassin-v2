import React, { useState } from 'react';
import { FolderSearch, FileSearch, Save } from 'lucide-react';
import { INPUT_STYLES } from './design-tokens';
import type { CategoryKey } from './design-tokens';

interface InputFieldProps {
  id: string;
  placeholder: string;
  defaultValue?: string;
  type?: string;
  className?: string;
  browseType?: 'folder' | 'file' | 'save';
  category?: CategoryKey; // Token system category
}

export const InputField: React.FC<InputFieldProps> = ({ id, placeholder, defaultValue = "", type = "text", className = "", browseType, category = 'neutral' }) => {
  const [loading, setLoading] = useState(false);

  const handleBrowse = async () => {
    setLoading(true);
    try {
      const API_BASE = import.meta.env.DEV ? "http://localhost:8000/api" : "/api";
      const res = await fetch(`${API_BASE}/browse?type=${browseType}`);
      const data = await res.json();
      
      if (data.success && data.path) {
        const inputEl = document.getElementById(id) as HTMLInputElement;
        if (inputEl) {
          inputEl.value = data.path;
          localStorage.setItem(id, data.path);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const ringStyle = INPUT_STYLES.focusRing(category);

  return (
    <div className="relative w-full">
      <input 
        id={id}
        type={type} 
        placeholder={placeholder}
        defaultValue={localStorage.getItem(id) || defaultValue}
        onChange={(e) => localStorage.setItem(id, e.target.value)}
        className={`${INPUT_STYLES.base} ${browseType ? 'pr-12' : ''} ${className}`}
        style={ringStyle}
      />
      {browseType && (
        <button
          type="button"
          onClick={handleBrowse}
          disabled={loading}
          className={`absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg text-white/50 hover:text-brand-primary hover:bg-brand-primary/10 transition-colors ${loading ? 'animate-pulse opacity-50 cursor-wait' : ''}`}
          title={`Browse for ${browseType}`}
        >
          {browseType === 'folder' ? <FolderSearch size={16} /> : 
           browseType === 'file' ? <FileSearch size={16} /> : 
           <Save size={16} />}
        </button>
      )}
    </div>
  );
};
