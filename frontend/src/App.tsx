import { useState, useEffect } from 'react'
import {
  Scissors, Target, MapPin, Combine,
  MonitorUp, Video, Camera, PenLine, VolumeX,
  FolderTree, Smartphone
} from 'lucide-react'
import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'
import { CommandPalette } from './components/ui'
import { DashboardPage } from './pages/DashboardPage'
import { MasterIngestPage } from './pages/MasterIngestPage'
import { MagicToolsPage } from './pages/MagicToolsPage'
import { CutToolsPage } from './pages/CutToolsPage'
import { ProcessPage } from './pages/ProcessPage'
import { ExportPage } from './pages/ExportPage'
import { TemplatesPage } from './pages/TemplatesPage'
import { SettingsPage } from './pages/SettingsPage'
import { ManualPage } from './pages/ManualPage'
import type {
  AppStatus, AppStats, AppContext, LogEntry, Toast,
  ProjectStatsResponse, BadWordsScanResponse
} from './types/api'

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000/api' : '/api'

const themes = [
  { name: 'Purple', primary: '#7e5cf5', bg: '#19122a' },
  { name: 'Rose', primary: '#f43f5e', bg: '#2a1215' },
  { name: 'Emerald', primary: '#10b981', bg: '#11231a' },
  { name: 'Cyan', primary: '#06b6d4', bg: '#102126' },
  { name: 'Amber', primary: '#f59e0b', bg: '#291d09' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isCmdPaletteOpen, setIsCmdPaletteOpen] = useState(false)
  const [status, setStatus] = useState<AppStatus>({ connected: false, message: 'Checking connection...' })
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [toasts, setToasts] = useState<Toast[]>([])
  const [stats, setStats] = useState<AppStats>({ name: '', fps: '', clips: 0, timecode: '' })
  const [templates, setTemplates] = useState<string[]>([])
  const [context, setContext] = useState<AppContext>({ project: '', timelines: [], current_timeline: '' })
  const [selectedMergeTimelines, setSelectedMergeTimelines] = useState<string[]>([])
  const [selectedBatchTimelines, setSelectedBatchTimelines] = useState<string[]>([])
  const [loading, setLoading] = useState<Record<string, boolean>>({})
  const [bwScan, setBwScan] = useState<BadWordsScanResponse | null>(null)
  const [bwColors, setBwColors] = useState<Record<string, boolean>>({ Red: true, Blue: true, Green: false })
  const [projectStats, setProjectStats] = useState<ProjectStatsResponse | null>(null)
  const [shotlistFormat, setShotlistFormat] = useState('csv')
  const [animationsEnabled, setAnimationsEnabled] = useState<boolean>(() =>
    localStorage.getItem('appAnimations') !== 'false'
  )
  const [favorites, setFavorites] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem('appFavorites_v2') || '[]') }
    catch { return [] }
  })

  useEffect(() => {
    localStorage.setItem('appAnimations', String(animationsEnabled))
  }, [animationsEnabled])

  useEffect(() => {
    localStorage.setItem('appFavorites_v2', JSON.stringify(favorites))
  }, [favorites])

  const applyTheme = (theme: typeof themes[0]) => {
    document.documentElement.style.setProperty('--app-primary', theme.primary)
    document.documentElement.style.setProperty('--app-bg-hex', theme.bg)
    localStorage.setItem('appTheme', theme.name)
  }

  useEffect(() => {
    const savedTheme = localStorage.getItem('appTheme') || 'Purple'
    const theme = themes.find(t => t.name === savedTheme)
    if (theme) applyTheme(theme)
    const toggleCmd = () => setIsCmdPaletteOpen(p => !p)
    window.addEventListener('toggle-cmd-palette', toggleCmd)
    return () => window.removeEventListener('toggle-cmd-palette', toggleCmd)
  }, [])

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`)
      const data = await res.json()
      setStatus({ connected: data.success, message: data.message })
    } catch {
      setStatus({ connected: false, message: 'Server unreachable' })
    }
  }

  const checkStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`)
      const data = await res.json()
      if (data.success) {
        setStats({ name: data.name, fps: data.fps, clips: data.clips, timecode: data.timecode })
      } else {
        setStats({ name: '', fps: '', clips: 0, timecode: '' })
      }
    } catch {
      setStats({ name: '', fps: '', clips: 0, timecode: '' })
    }
  }

  const fetchContext = async () => {
    try {
      const res = await fetch(`${API_BASE}/context`)
      const data = await res.json()
      if (data.success) {
        setContext({ project: data.project, timelines: data.timelines, current_timeline: data.current_timeline })
      }
    } catch { /* ignore */ }
  }

  const fetchTemplates = async () => {
    try {
      const res = await fetch(`${API_BASE}/templates`)
      const data = await res.json()
      if (data.success) setTemplates(data.templates)
    } catch { /* ignore */ }
  }

  useEffect(() => {
    checkStatus()
    checkStats()
    fetchContext()
    fetchTemplates()
    const statInterval = setInterval(checkStats, 3000)
    return () => clearInterval(statInterval)
  }, [])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'SELECT') return
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault()
        runTask('snapshot', {}, 'snapshot')
      }
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 's') {
        e.preventDefault()
        setLoading(prev => ({ ...prev, bw_scan: true }))
        fetch(`${API_BASE}/badwords/scan`)
          .then(res => res.json())
          .then(data => {
            setBwScan(data)
            if (data.success) addLog(`Found ${data.total_markers} markers on '${data.timeline_name}'`, 'success')
            else addLog(data.message, 'error')
          })
          .catch(() => addLog('Failed to scan markers', 'error'))
          .finally(() => setLoading(prev => ({ ...prev, bw_scan: false })))
      }
      if ((e.metaKey || e.ctrlKey) && ['1', '2', '3', '4', '5', '6'].includes(e.key)) {
        e.preventDefault()
        const tabs = ['magic', 'cut', 'process', 'export', 'templates', 'help']
        setActiveTab(tabs[parseInt(e.key) - 1])
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const toggleFavorite = (id: string) => {
    setFavorites(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id])
  }

  const addLog = (msg: string, type: 'info' | 'success' | 'error') => {
    const id = Date.now() + Math.random()
    setLogs(prev => [{ id: String(id), msg, type, time: new Date().toLocaleTimeString() }, ...prev].slice(0, 10))
    setToasts(prev => [...prev, { id, msg, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000)
  }

  const handleConnect = async () => {
    addLog('Connecting to DaVinci Resolve...', 'info')
    try {
      const res = await fetch(`${API_BASE}/connect`, { method: 'POST' })
      const data = await res.json()
      setStatus({ connected: data.success, message: data.message })
      addLog(data.message, data.success ? 'success' : 'error')
      if (data.success) { checkStats(); fetchContext(); fetchTemplates() }
    } catch {
      addLog('Failed to reach Python backend.', 'error')
    }
  }

  const handleSetTimeline = async (timeline_name: string) => {
    addLog(`Switching to timeline: ${timeline_name}`, 'info')
    try {
      const res = await fetch(`${API_BASE}/set_context`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timeline_name })
      })
      const data = await res.json()
      addLog(data.message, data.success ? 'success' : 'error')
      if (data.success) { checkStats(); fetchContext() }
    } catch {
      addLog('Failed to switch timeline', 'error')
    }
  }

  const runTask = async (endpoint: string, payload: Record<string, unknown> = {}, buttonId: string) => {
    setLoading(prev => ({ ...prev, [buttonId]: true }))
    addLog('Running task...', 'info')
    try {
      const res = await fetch(`${API_BASE}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (data.success && endpoint === 'youtube_chapters') {
        try {
          await navigator.clipboard.writeText(data.message)
          addLog('Chapters copied to clipboard!', 'success')
        } catch {
          addLog('Generated chapters successfully (could not auto-copy)', 'success')
        }
      } else {
        addLog(data.message, data.success ? 'success' : 'error')
      }
      checkStats()
      fetchContext()
    } catch (e: unknown) {
      addLog(`Error: ${e instanceof Error ? e.message : 'Unknown error'}`, 'error')
    } finally {
      setLoading(prev => ({ ...prev, [buttonId]: false }))
    }
  }

  const handleCreateMasterFolder = async () => {
    const parentDir = (document.getElementById('createParentFolderInput') as HTMLInputElement)?.value?.trim()
    const projName = (document.getElementById('createProjectNameInput') as HTMLInputElement)?.value?.trim()
    const clientName = (document.getElementById('createClientNameInput') as HTMLInputElement)?.value?.trim() || ''
    const projType = (document.getElementById('createPresetSelect') as HTMLSelectElement)?.value || 'Standard Video & Film'
    const customDate = (document.getElementById('createDateInput') as HTMLInputElement)?.value?.trim() || ''

    if (!parentDir || !projName) {
      addLog('Please specify a Parent Directory and Project Name.', 'error')
      return
    }
    setLoading(prev => ({ ...prev, create_master_folder: true }))
    addLog('Creating Master Folder structure on disk...', 'info')
    try {
      const res = await fetch(`${API_BASE}/create_master_folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parent_dir: parentDir, project_name: projName, client_name: clientName, project_type: projType, custom_date: customDate })
      })
      const data = await res.json()
      if (data.success) {
        addLog(data.message, 'success')
        const masterInputEl = document.getElementById('masterFolderInput') as HTMLInputElement
        if (masterInputEl && data.folder_path) masterInputEl.value = data.folder_path
      } else {
        addLog(data.message || 'Failed to create Master Folder', 'error')
      }
    } catch (e: unknown) {
      addLog(`Error: ${e instanceof Error ? e.message : 'Unknown error'}`, 'error')
    } finally {
      setLoading(prev => ({ ...prev, create_master_folder: false }))
    }
  }

  const isDashboard = activeTab === 'dashboard'
  const sharedProps = { isDashboard, favorites, toggleFavorite, loading, context, runTask, addLog }

  return (
    <div className="flex h-screen bg-brand-bg font-sans overflow-hidden text-slate-200">
      {animationsEnabled && (
        <div className="glow-bg">
          <div className="glow-orb-1" />
          <div className="glow-orb-2" />
        </div>
      )}

      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} logs={logs} setLogs={setLogs} />

      <div className="flex-1 flex flex-col relative h-screen overflow-y-auto overflow-x-hidden scroll-smooth">
        <Header
          status={status}
          handleConnect={handleConnect}
          context={context}
          handleSetTimeline={handleSetTimeline}
          stats={stats}
          activeTab={activeTab}
        />

        <div className="flex-1 w-full max-w-7xl mx-auto px-6 md:px-12 lg:px-20 pb-48 pt-4">
          {isDashboard && (
            <DashboardPage
              API_BASE={API_BASE}
              favorites={favorites}
              setFavorites={setFavorites}
              loading={loading}
              setLoading={setLoading}
              projectStats={projectStats}
              setProjectStats={setProjectStats}
              addLog={addLog}
            />
          )}

          {(activeTab === 'master_ingest' || isDashboard) && (
            <MasterIngestPage
              {...sharedProps}
              handleCreateMasterFolder={handleCreateMasterFolder}
            />
          )}

          {(activeTab === 'magic' || isDashboard) && (
            <MagicToolsPage
              {...sharedProps}
              API_BASE={API_BASE}
              setLoading={setLoading}
              bwScan={bwScan}
              setBwScan={setBwScan}
              bwColors={bwColors}
              setBwColors={setBwColors}
            />
          )}

          {(activeTab === 'cut' || isDashboard) && (
            <CutToolsPage {...sharedProps} />
          )}

          {(activeTab === 'process' || isDashboard) && (
            <ProcessPage
              {...sharedProps}
              selectedMergeTimelines={selectedMergeTimelines}
              setSelectedMergeTimelines={setSelectedMergeTimelines}
            />
          )}

          {(activeTab === 'export' || isDashboard) && (
            <ExportPage
              {...sharedProps}
              API_BASE={API_BASE}
              selectedBatchTimelines={selectedBatchTimelines}
              setSelectedBatchTimelines={setSelectedBatchTimelines}
              shotlistFormat={shotlistFormat}
              setShotlistFormat={setShotlistFormat}
            />
          )}

          {activeTab === 'templates' && (
            <TemplatesPage
              templates={templates}
              fetchTemplates={fetchTemplates}
              loading={loading}
              setLoading={setLoading}
              runTask={runTask}
              addLog={addLog}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsPage
              animationsEnabled={animationsEnabled}
              setAnimationsEnabled={setAnimationsEnabled}
              setFavorites={setFavorites}
              setLogs={setLogs}
              applyTheme={applyTheme}
              addLog={addLog}
            />
          )}

          {activeTab === 'manual' && <ManualPage />}
        </div>
      </div>

      <div className="absolute top-24 right-8 z-[100] flex flex-col gap-3 pointer-events-none">
        {toasts.map(t => (
          <div key={t.id} className={`animate-in slide-in-from-right-8 fade-in duration-300 pointer-events-auto flex items-center gap-3 px-5 py-3 rounded-2xl shadow-2xl border backdrop-blur-xl ${
            t.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${t.type === 'success' ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]' : 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)]'}`} />
            <span className="text-sm font-medium">{t.msg}</span>
          </div>
        ))}
      </div>

      <CommandPalette
        isOpen={isCmdPaletteOpen}
        onClose={() => setIsCmdPaletteOpen(false)}
        actions={[
          { id: 'snapshot', title: 'Timeline Snapshot', icon: <Camera size={16} />, keywords: ['backup', 'save'], perform: () => runTask('snapshot', {}, 'snapshot') },
          { id: 'magic_bin_organizer', title: 'Magic Bin Organizer', icon: <FolderTree size={16} />, keywords: ['organize', 'folder'], perform: () => runTask('organize_bins', {}, 'magic_bins') },
          { id: 'silence_remover', title: 'Silence Remover', icon: <VolumeX size={16} />, keywords: ['cut', 'dead space'], perform: () => runTask('silence_remove', {}, 'silence') },
          { id: 'batch_clip_renamer', title: 'Batch Clip Renamer', icon: <PenLine size={16} />, perform: () => setActiveTab('magic') },
          { id: 'social_media_reframe', title: 'Social Media Reframe', icon: <Smartphone size={16} />, perform: () => runTask('social_reframe', { format: '9:16' }, 'magic_reframe_916') },
          { id: 'adjustment_layer', title: 'Quick Adjustment Layer', icon: <Combine size={16} />, keywords: ['fx', 'color', 'grade'], perform: () => runTask('add_adjustment_layer', {}, 'magic_adj') },
          { id: 'timecode_cutter', title: 'Timecode Cutter', icon: <Scissors size={16} />, perform: () => setActiveTab('cut') },
          { id: 'markers_to_timeline', title: 'Markers to Timeline', icon: <MapPin size={16} />, perform: () => setActiveTab('cut') },
          { id: 'batch_timeline_render', title: 'Batch Timeline Render', icon: <MonitorUp size={16} />, perform: () => setActiveTab('export') },
          { id: 'auto_youtube_chapters', title: 'Auto YouTube Chapters', icon: <Video size={16} />, perform: () => runTask('youtube_chapters', {}, 'chapters') },
          { id: 'shotlist_generator', title: 'Client Shotlist / Document Exporter', icon: <Target size={16} />, keywords: ['csv', 'excel', 'doc', 'word'], perform: () => setActiveTab('export') },
        ]}
      />

      <div className="absolute bottom-6 right-8 flex items-center gap-3 bg-black/40 backdrop-blur-md border border-white/5 rounded-full py-2 px-4 shadow-xl pointer-events-none hidden md:flex">
        <img src="/logo.jpg" alt="Clip Assassin Logo" className="w-6 h-6 rounded-md shadow-sm border border-brand-primary/20" />
        <div className="flex flex-col">
          <span className="text-[11px] font-bold text-white/80 tracking-wide leading-tight">Clip Assassin</span>
          <span className="text-[9px] font-semibold text-brand-primary uppercase tracking-widest leading-tight">Version 2.0.1</span>
        </div>
      </div>
    </div>
  )
}
