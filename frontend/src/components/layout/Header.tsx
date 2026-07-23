import React, { useState } from 'react';
import { 
  Zap, Clapperboard, Folder, ChevronDown 
} from 'lucide-react';

interface HeaderProps {
  status: { connected: boolean; message: string };
  handleConnect: () => void | Promise<void>;
  context: { project: string; timelines: string[]; current_timeline: string };
  handleSetTimeline: (name: string) => void;
  stats: { name: string; fps: string; clips: number; timecode: string };
  activeTab?: string;
}

export const Header: React.FC<HeaderProps> = ({
  status, handleConnect, context, handleSetTimeline, stats, activeTab
}) => {
  const [showContextDropdown, setShowContextDropdown] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const tabNames: Record<string, string> = {
    dashboard: 'Dashboard',
    master_ingest: 'Master Ingest',
    cut: 'Cut & Trim',
    magic: 'Magic Tools',
    process: 'Process',
    export: 'Export',
    templates: 'Templates',
    settings: 'Settings',
    manual: 'User Manual'
  };
  const activeTabName = activeTab ? tabNames[activeTab] : '';

  const onConnectClick = async () => {
    setIsConnecting(true);
    try {
      await handleConnect();
    } finally {
      setIsConnecting(false);
    }
  };

  let iconBgClass = '';
  let iconColor = '';
  let tooltip = '';
  let showRedDot = false;
  let boxShadow = 'none';

  if (isConnecting) {
    iconBgClass = 'bg-[#F59E0B]/10';
    iconColor = 'text-[#F59E0B]';
    tooltip = 'Reconnecting...';
    boxShadow = '0 0 15px rgba(245,158,11,0.4)';
  } else if (status.connected) {
    iconBgClass = 'bg-[#10B981]/10';
    iconColor = 'text-[#10B981]';
    tooltip = 'Connected to DaVinci Resolve';
    boxShadow = '0 0 15px rgba(16,185,129,0.3)';
  } else {
    iconBgClass = 'bg-[#F43F5E]/10';
    iconColor = 'text-[#F43F5E]';
    tooltip = 'Disconnected — click to reconnect';
    showRedDot = true;
    boxShadow = 'none';
  }

  return (
    <div className="flex items-center justify-between w-full p-6 relative">
      
      {/* Target Context Selector (Left) */}
      <div className="relative z-50">
        <button 
          onClick={() => setShowContextDropdown(!showContextDropdown)}
          className="flex flex-col bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl py-2 px-5 shadow-xl hover:bg-white/10 transition-colors text-left min-w-[200px] md:min-w-[240px]"
        >
          <div className="flex items-center gap-1.5 text-[10px] text-white/60 font-semibold uppercase tracking-widest mb-1">
            <Folder size={12} className="text-brand-primary" /> {context.project || "No Project"}
          </div>
          <div className="flex items-center justify-between text-sm text-white/90">
            <span className="truncate max-w-[150px] md:max-w-[180px] font-medium">{context.current_timeline || "No Timeline"}</span>
            <ChevronDown size={14} className={`text-white/40 transition-transform ${showContextDropdown ? 'rotate-180' : ''}`} />
          </div>
        </button>
        
        {showContextDropdown && context.timelines.length > 0 && (
          <div className="absolute top-full left-0 mt-3 w-72 bg-[#150F22] border border-white/10 rounded-2xl shadow-2xl py-2 max-h-64 overflow-y-auto z-50">
            <div className="px-4 pb-2 mb-2 border-b border-white/5 text-[10px] text-white/40 uppercase tracking-widest font-semibold">
              Switch Timeline Target
            </div>
            {context.timelines.map(t => (
              <button
                key={t}
                onClick={() => {
                  handleSetTimeline(t);
                  setShowContextDropdown(false);
                }}
                className={`w-full text-left px-5 py-2.5 text-xs transition-colors hover:bg-white/5 flex items-center gap-3 ${t === context.current_timeline ? 'text-brand-primary font-semibold' : 'text-white/80'}`}
              >
                <Clapperboard size={14} className={t === context.current_timeline ? 'text-brand-primary' : 'text-white/30'} />
                <span className="truncate">{t}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Active Tab Name (Middle) */}
      <div className="absolute left-1/2 -translate-x-1/2 pointer-events-none hidden md:flex items-center gap-2 bg-white/5 backdrop-blur-md border border-white/10 px-4 py-1.5 rounded-full text-xs font-bold text-white/80 tracking-[0.2em] uppercase shadow-lg">
        <span className="w-1.5 h-1.5 rounded-full bg-brand-primary animate-pulse"></span>
        {activeTabName}
      </div>

      {/* Stats & Connection (Right) */}
      <div className="flex items-center gap-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl py-2 pl-6 pr-2 shadow-xl">
        
        {/* Live Timeline Stats */}
        {stats.name ? (
          <div className="flex items-center gap-4 hidden lg:flex text-xs text-white/60 font-mono tracking-wide">
            <span>{stats.clips} Clips</span>
            <div className="w-px h-3 bg-white/20"></div>
            <span>{stats.fps}fps</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-xs text-white/30 font-mono hidden lg:flex">
            <span>No Active Timeline</span>
          </div>
        )}

        {/* Connection Button */}
        <button 
          onClick={onConnectClick}
          className={`flex items-center justify-center w-10 h-10 shrink-0 rounded-full transition-all relative group border border-white/5 ${iconBgClass} ${isConnecting ? 'animate-pulse' : ''}`}
          style={{ boxShadow }}
        >
          <Zap size={16} fill="currentColor" className={iconColor} />
          {showRedDot && (
            <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-[#F43F5E] border-2 border-[#150F22] rounded-full"></span>
          )}
          
          <div className="absolute top-12 right-0 opacity-0 group-hover:opacity-100 transition-opacity bg-black/90 border border-white/10 px-3 py-2 rounded-xl text-xs whitespace-nowrap pointer-events-none text-white/80 shadow-2xl z-50">
            {tooltip}
          </div>
        </button>

      </div>
    </div>
  );
};
