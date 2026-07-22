import React from 'react';
import { 
  Sparkles, Library, Scissors, Combine, MonitorUp, BookOpen, Activity, CheckCircle2, XCircle, Info, FolderPlus
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  logs: {msg: string, type: 'info'|'success'|'error'}[];
  setLogs: (logs: any) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, logs, setLogs }) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: <Activity size={18}/> },
    { id: 'master_ingest', label: 'Master Ingest', icon: <FolderPlus size={18}/> },
    { id: 'cut', label: 'Cut & Trim', icon: <Scissors size={18}/> },
    { id: 'magic', label: 'Magic Tools', icon: <Sparkles size={18}/> },
    { id: 'process', label: 'Process', icon: <Combine size={18}/> },
    { id: 'export', label: 'Export', icon: <MonitorUp size={18}/> },
    { id: 'templates', label: 'Templates', icon: <Library size={18}/> },
    { id: 'manual', label: 'User Manual', icon: <BookOpen size={18}/> },
    { id: 'settings', label: 'Settings', icon: <Info size={18}/> }
  ];

  return (
    <div className="w-64 h-screen shrink-0 bg-black/40 backdrop-blur-3xl border-r border-white/5 p-6 flex flex-col z-40 hidden md:flex">
      <div className="flex items-center gap-3 mb-10 pl-2">
        <img src="/logo.jpg" alt="Clip Assassin" className="w-10 h-10 rounded-lg shadow-lg border border-brand-primary/30" />
        <div className="flex flex-col">
          <h1 className="text-lg font-bold tracking-tight text-white/90">Clip Assassin</h1>
          <p className="text-[8px] font-medium text-brand-primary uppercase tracking-widest mt-0.5">Automate DaVinci Resolve</p>
        </div>
      </div>
      
      <div className="space-y-2 mb-8">
        <div className="text-[10px] font-semibold text-white/30 uppercase tracking-widest pl-2 mb-4 mt-2">Tools</div>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-300 text-sm font-medium
              ${activeTab === t.id 
                ? 'bg-brand-primary/10 text-brand-primary shadow-[inset_0_0_0_1px_rgba(var(--brand-primary),0.2)]' 
                : 'text-white/50 hover:bg-white/5 hover:text-white/80'}`}
          >
            <div className={`${activeTab === t.id ? 'text-brand-primary' : 'text-white/40'}`}>
              {t.icon}
            </div>
            {t.label}
          </button>
        ))}
      </div>
      
      {/* Sidebar Mission Log */}
      <div className="flex-1 flex flex-col min-h-0 bg-black/20 rounded-2xl border border-white/5 p-3 overflow-hidden">
        <div className="flex items-center justify-between mb-3 px-1 shrink-0">
          <span className="text-[10px] font-semibold text-brand-primary uppercase tracking-widest flex items-center gap-1.5">
            <Activity size={12}/> Mission Log
          </span>
          <button onClick={() => setLogs([])} className="text-[9px] text-white/30 hover:text-white transition-colors uppercase tracking-widest font-semibold">Clear</button>
        </div>
        <div className="flex-1 overflow-y-auto px-1 space-y-2 font-mono text-[10px] scrollbar-thin">
          {logs.length === 0 && <p className="text-white/20 italic">Awaiting commands...</p>}
          {logs.map((log, i) => (
            <div key={i} className="flex gap-1.5 leading-relaxed">
              {log.type === 'success' && <CheckCircle2 size={12} className="text-emerald-400 shrink-0 mt-0.5" />}
              {log.type === 'error' && <XCircle size={12} className="text-rose-400 shrink-0 mt-0.5" />}
              {log.type === 'info' && <Info size={12} className="text-sky-400 shrink-0 mt-0.5" />}
              <span className={
                log.type === 'success' ? 'text-emerald-400/90' : 
                log.type === 'error' ? 'text-rose-400/90' : 'text-sky-400/90'
              }>
                {log.msg}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 shrink-0 pt-4 border-t border-white/5 flex flex-col gap-1 items-center">
        <div className="text-[10px] text-white/40 font-semibold tracking-widest uppercase">
          Version 2.0.1
        </div>
        <div className="text-[9px] text-white/20 font-medium tracking-widest uppercase">
          BY ZABID AL MUTTAKI
        </div>
      </div>
    </div>
  );
};
