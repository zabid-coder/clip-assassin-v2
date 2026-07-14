import React, { useState, useEffect, useRef } from 'react';
import { Search, Command } from 'lucide-react';

export interface CommandAction {
  id: string;
  title: string;
  icon?: React.ReactNode;
  perform: () => void;
  keywords?: string[];
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  actions: CommandAction[];
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose, actions }) => {
  const [search, setSearch] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setSearch('');
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          window.dispatchEvent(new CustomEvent('toggle-cmd-palette'));
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filteredActions = actions.filter(action => {
    const query = search.toLowerCase();
    return action.title.toLowerCase().includes(query) || 
           action.keywords?.some(k => k.toLowerCase().includes(query));
  });

  return (
    <div className="fixed inset-0 z-[200] flex items-start justify-center pt-[15vh] px-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200" 
        onClick={onClose}
      />
      
      {/* Palette */}
      <div className="relative w-full max-w-xl bg-brand-card/90 backdrop-blur-2xl border border-brand-primary/30 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200">
        <div className="flex items-center px-4 py-4 border-b border-white/5">
          <Search className="text-brand-primary w-5 h-5 mr-3" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 bg-transparent border-none text-white focus:outline-none focus:ring-0 placeholder-white/40 text-lg"
            placeholder="Search tools or commands..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="flex items-center gap-1 text-xs text-white/40 font-mono bg-white/5 px-2 py-1 rounded">
            <span>ESC</span>
          </div>
        </div>
        
        <div className="max-h-[60vh] overflow-y-auto p-2">
          {filteredActions.length === 0 ? (
            <div className="py-12 text-center text-white/40">
              <Command className="w-8 h-8 mx-auto mb-3 opacity-20" />
              <p>No tools found for "{search}"</p>
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {filteredActions.map((action) => (
                <button
                  key={action.id}
                  className="flex items-center gap-3 w-full px-4 py-3 rounded-xl hover:bg-brand-primary/20 text-left transition-colors group"
                  onClick={() => {
                    action.perform();
                    onClose();
                  }}
                >
                  <div className="text-brand-primary group-hover:scale-110 transition-transform">
                    {action.icon}
                  </div>
                  <span className="flex-1 font-medium text-white/90">{action.title}</span>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-xs bg-brand-primary/20 text-brand-primary px-2 py-1 rounded">Run</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
