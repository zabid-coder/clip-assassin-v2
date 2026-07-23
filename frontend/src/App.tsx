import { useState, useEffect } from 'react'
import { 
  Scissors, Target, MapPin, Flag, Combine, Droplet, 
  MonitorUp, Image as ImageIcon, FileSpreadsheet, Video, 
  User, Mail, Sparkles, Type, FolderTree, Smartphone, Library, Box, Wand2,
  Camera, PenLine, VolumeX, AudioLines, BarChart3, Link, UploadCloud,
  Activity, BookOpen, FolderPlus
} from 'lucide-react'
import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'
import { ActionButton, FeatureCard, InputField, SelectField, CommandPalette } from './components/ui'

const API_BASE = import.meta.env.DEV ? "http://localhost:8000/api" : "/api"

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
  const [status, setStatus] = useState({ connected: false, message: 'Checking connection...' })
  const [logs, setLogs] = useState<{msg: string, type: 'info'|'success'|'error'}[]>([])
  const [toasts, setToasts] = useState<{id: number, msg: string, type: 'success'|'error'|'info'}[]>([])
  const [stats, setStats] = useState({ name: '', fps: '', clips: 0, timecode: '' })
  const [templates, setTemplates] = useState<string[]>([])
  
  const [context, setContext] = useState<{project: string, timelines: string[], current_timeline: string}>({
    project: '', timelines: [], current_timeline: ''
  })
  
  const [selectedMergeTimelines, setSelectedMergeTimelines] = useState<string[]>([])
  const [selectedBatchTimelines, setSelectedBatchTimelines] = useState<string[]>([])
  
  // Track loading state for each button by ID
  const [loading, setLoading] = useState<Record<string, boolean>>({})

  // BadWords scan results
  const [bwScan, setBwScan] = useState<any>(null)
  const [bwColors, setBwColors] = useState<Record<string, boolean>>({ Red: true, Blue: true, Green: false })

  // Project stats
  const [projectStats, setProjectStats] = useState<any>(null)
  
  // Favorites
  const [favorites, setFavorites] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem('appFavorites_v2') || '[]') }
    catch { return [] }
  })

  // App Preferences
  const [animationsEnabled, setAnimationsEnabled] = useState<boolean>(() => {
    return localStorage.getItem('appAnimations') !== 'false'
  })

  useEffect(() => {
    localStorage.setItem('appAnimations', String(animationsEnabled))
  }, [animationsEnabled])
  
  // Export Presets
  // Removed unused preset states
  
  // Shotlist
  const [shotlistFormat, setShotlistFormat] = useState('csv')

  // Theme Loader
  useEffect(() => {
    const savedTheme = localStorage.getItem('appTheme') || 'Purple'
    const theme = themes.find(t => t.name === savedTheme)
    if (theme) applyTheme(theme)
    
    const toggleCmd = () => setIsCmdPaletteOpen(p => !p)
    window.addEventListener('toggle-cmd-palette', toggleCmd)
    return () => window.removeEventListener('toggle-cmd-palette', toggleCmd)
  }, [])

  const applyTheme = (theme: typeof themes[0]) => {
    document.documentElement.style.setProperty('--app-primary', theme.primary)
    document.documentElement.style.setProperty('--app-bg-hex', theme.bg)
    localStorage.setItem('appTheme', theme.name)
  }

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
    } catch {
      // Ignore
    }
  }

  const fetchTemplates = async () => {
    try {
      const res = await fetch(`${API_BASE}/templates`)
      const data = await res.json()
      if (data.success) {
        setTemplates(data.templates)
      }
    } catch {
      console.error("Failed to fetch templates")
    }
  }

  useEffect(() => {
    checkStatus()
    checkStats()
    fetchContext()
    fetchTemplates()

    const statInterval = setInterval(checkStats, 3000)
    return () => clearInterval(statInterval)
  }, [])

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input
      if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'SELECT') return
      
      // Cmd/Ctrl + S for Snapshot
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault()
        runTask('snapshot', {}, 'snapshot')
      }
      // Cmd/Ctrl + Shift + S for BadWords Scan
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
      
      // Cmd/Ctrl + 1-6 for Tabs
      if ((e.metaKey || e.ctrlKey) && ['1','2','3','4','5','6'].includes(e.key)) {
        e.preventDefault()
        const tabs = ['magic', 'cut', 'process', 'export', 'templates', 'help']
        setActiveTab(tabs[parseInt(e.key) - 1])
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Save favorites to localStorage
  useEffect(() => {
    localStorage.setItem('appFavorites_v2', JSON.stringify(favorites))
  }, [favorites])
  
  const toggleFavorite = (id: string) => {
    setFavorites(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id])
  }



  const addLog = (msg: string, type: 'info'|'success'|'error') => {
    const id = Date.now() + Math.random()
    setLogs(prev => {
      const newLogs = [{ id: String(id), msg, type, time: new Date().toLocaleTimeString() }, ...prev]
      return newLogs.slice(0, 10) // Limit to last 10 entries
    })
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
      if (data.success) {
        checkStats()
        fetchContext()
        fetchTemplates()
      }
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
      if (data.success) {
        checkStats()
        fetchContext()
      }
    } catch {
      addLog('Failed to switch timeline', 'error')
    }
  }

  const runTask = async (endpoint: string, payload: any = {}, buttonId: string) => {
    setLoading(prev => ({ ...prev, [buttonId]: true }))
    addLog(`Running task...`, 'info')
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
          addLog('Chapters copied to clipboard! 📋', 'success')
        } catch (err) {
          // Fallback if clipboard fails
          addLog('Generated chapters successfully (could not auto-copy)', 'success')
          console.error('Clipboard copy failed:', err)
        }
      } else {
        addLog(data.message, data.success ? 'success' : 'error')
      }
      
      checkStats()
      fetchContext()
    } catch (e: any) {
      addLog(`Error: ${e.message}`, 'error')
    } finally {
      setLoading(prev => ({ ...prev, [buttonId]: false }))
    }
  }

  const handleCreateMasterFolder = async () => {
    const parentEl = document.getElementById('createParentFolderInput') as HTMLInputElement;
    const projEl = document.getElementById('createProjectNameInput') as HTMLInputElement;
    const clientEl = document.getElementById('createClientNameInput') as HTMLInputElement;
    const presetEl = document.getElementById('createPresetSelect') as HTMLSelectElement;
    const dateEl = document.getElementById('createDateInput') as HTMLInputElement;

    const parentDir = parentEl?.value?.trim();
    const projName = projEl?.value?.trim();
    const clientName = clientEl?.value?.trim() || "";
    const projType = presetEl?.value || "Standard Video & Film";
    const customDate = dateEl?.value?.trim() || "";

    if (!parentDir || !projName) {
      addLog('Please specify a Parent Directory and Project Name.', 'error');
      return;
    }

    setLoading(prev => ({ ...prev, create_master_folder: true }));
    addLog('Creating Master Folder structure on disk...', 'info');

    try {
      const res = await fetch(`${API_BASE}/create_master_folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_dir: parentDir,
          project_name: projName,
          client_name: clientName,
          project_type: projType,
          custom_date: customDate
        })
      });
      const data = await res.json();
      if (data.success) {
        addLog(data.message, 'success');
        const masterInputEl = document.getElementById('masterFolderInput') as HTMLInputElement;
        if (masterInputEl && data.folder_path) {
          masterInputEl.value = data.folder_path;
        }
      } else {
        addLog(data.message || 'Failed to create Master Folder', 'error');
      }
    } catch (e: any) {
      addLog(`Error: ${e.message}`, 'error');
    } finally {
      setLoading(prev => ({ ...prev, create_master_folder: false }));
    }
  }

  return (
    <div className="flex h-screen bg-brand-bg font-sans overflow-hidden text-slate-200">
      


      {/* Sidebar */}
      {/* Background Glows */}
      {animationsEnabled && (
        <div className="glow-bg">
          <div className="glow-orb-1"></div>
          <div className="glow-orb-2"></div>
        </div>
      )}

      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} logs={logs} setLogs={setLogs} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative h-screen overflow-y-auto overflow-x-hidden scroll-smooth">
        <Header 
          status={status} 
          handleConnect={handleConnect} 
          context={context} 
          handleSetTimeline={handleSetTimeline}
          stats={stats}
          activeTab={activeTab}
        />

        {/* Content Container */}
        <div className="flex-1 w-full max-w-7xl mx-auto px-6 md:px-12 lg:px-20 pb-48 pt-4">

          {/* Dashboard Welcome Message */}
          {activeTab === 'dashboard' && (
            <div className="mb-8 p-6 bg-brand-primary/10 border border-brand-primary/20 rounded-2xl animate-in fade-in slide-in-from-top-4 duration-500 flex flex-col md:flex-row items-center gap-6 text-center md:text-left">
              <div className="w-16 h-16 bg-brand-primary/20 rounded-full flex items-center justify-center shrink-0 mx-auto md:mx-0">
                <Sparkles className="text-brand-primary" size={32} />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-white mb-2">Welcome to your Dashboard</h2>
                <p className="text-white/60 text-sm max-w-2xl">
                  This is your personalized workspace. By default, it only shows your <strong>Project Stats</strong>. 
                  You can add any tool from the other tabs to this dashboard by clicking the <strong className="text-white">Pin icon</strong> in the top right corner of its card!
                </p>
              </div>
              
              {favorites.length > 0 && (
                <div className="shrink-0 mt-4 md:mt-0">
                  <button 
                    onClick={() => setFavorites([])}
                    className="px-4 py-2 bg-rose-500/10 text-rose-400 hover:bg-rose-500 hover:text-white rounded-xl text-sm font-medium transition-colors border border-rose-500/20 shadow-lg shadow-rose-900/20"
                  >
                    Reset Dashboard
                  </button>
                </div>
              )}
            </div>
          )}

          {/* --- TAB: TEMPLATES --- */}
          {activeTab === 'templates' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
              
              <div className="flex justify-between items-end mb-2">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Library className="text-brand-primary" /> Asset Library
                  </h2>
                  <p className="text-xs text-white/50 mt-1">Imports .drfx templates from your plugin folder straight into the Media Pool.</p>
                </div>
                <button onClick={fetchTemplates} className="text-xs text-brand-primary hover:text-white transition-colors">Refresh Library</button>
              </div>

              <div 
                className={`transition-all duration-300 ${loading['drop'] ? 'ring-2 ring-brand-primary' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setLoading(prev => ({...prev, drop: true})) }}
                onDragLeave={(e) => { e.preventDefault(); setLoading(prev => ({...prev, drop: false})) }}
                onDrop={async (e) => {
                  e.preventDefault();
                  setLoading(prev => ({...prev, drop: false}))
                  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    addLog("Browser security prevents reading the absolute path. Please place the file in the 'templates' folder directly.", "error")
                  }
                }}
              >
                {templates.length === 0 ? (
                  <div className={`bg-black/20 border border-white/5 border-dashed rounded-2xl p-12 text-center text-white/40 transition-colors ${loading['drop'] ? 'bg-brand-primary/10 border-brand-primary/50 text-brand-primary/80' : ''}`}>
                    <UploadCloud size={40} className="mx-auto mb-3 opacity-40" />
                    <p className="text-sm font-medium">Drop templates here</p>
                    <p className="text-xs mt-1 opacity-70">Add .drfx, images, or audio to the templates folder.</p>
                  </div>
                ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
                  {templates.map(fileName => (
                    <div key={fileName} className="bg-black/20 backdrop-blur-md border border-white/5 rounded-2xl p-5 hover:border-brand-primary/30 hover:bg-black/40 transition-all flex flex-col justify-between h-[140px]">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-brand-primary/10 text-brand-primary rounded-lg shrink-0">
                          <Box size={16} />
                        </div>
                        <p className="text-xs font-semibold text-white/90 break-words line-clamp-2">{fileName}</p>
                      </div>
                      <ActionButton 
                        text="Import to Media Pool" 
                        category="organize" variant="secondary"
                        isLoading={loading[`import_${fileName}`]}
                        onClick={() => runTask('import_template', { template_name: fileName }, `import_${fileName}`)}
                      />
                    </div>
                  ))}
                </div>
                )}
              </div>
            </div>
          )}
          
          {/* --- TAB: MASTER INGEST --- */}
          {(activeTab === 'master_ingest' || activeTab === 'dashboard') && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6 mb-6">
              
              {/* Top Section: Master Folder Setup */}
              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('create_master_folder')} 
                id="create_master_folder"
                isFavorite={favorites.includes('create_master_folder')}
                onToggleFavorite={() => toggleFavorite("create_master_folder")} 
                description="Create a standardized project directory template on disk before copying card footage."
                className="ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Master Folder Setup" 
                icon={<FolderTree size={18} />} 
                category="magic"
                helpText="Creates a clean, organized directory structure (Raw Footages, DaVinci Database, Audio, Graphics, Exports) on disk with automatic date and client prefixing."
              >
                <div className="flex flex-col gap-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="text-xs font-semibold text-white/70 mb-1.5 block">Parent Directory (Disk Root) *</label>
                      <InputField 
                        id="createParentFolderInput" 
                        browseType="folder" 
                        placeholder="/Users/audiovisual/Desktop" 
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-white/70 mb-1.5 block">Project Name *</label>
                      <InputField 
                        id="createProjectNameInput" 
                        placeholder="e.g. UNICEF_WASH_Visit" 
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-white/70 mb-1.5 block">Project Date (YYYY-MM-DD)</label>
                      <InputField 
                        id="createDateInput" 
                        type="date"
                        placeholder="YYYY-MM-DD" 
                        defaultValue={new Date().toISOString().split('T')[0]}
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-white/70 mb-1.5 block">Client / Agency (Optional)</label>
                      <InputField 
                        id="createClientNameInput" 
                        placeholder="e.g. UNICEF" 
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="text-xs font-semibold text-white/70 mb-1.5 block">Folder Template Preset</label>
                      <SelectField 
                        id="createPresetSelect"
                        options={['Standard Video & Film', 'Social Media & Reels', 'Commercial / Corporate']}
                      />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <div className="w-full md:w-1/3">
                      <ActionButton 
                        text="Create Master Folder" 
                        category="magic" variant="primary"
                        isLoading={loading['create_master_folder']}
                        onClick={handleCreateMasterFolder}
                      />
                    </div>
                  </div>
                </div>
              </FeatureCard>

              {/* Bottom Section: Auto Ingest */}
              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('master_ingest')} 
                id="master_ingest"
                isFavorite={favorites.includes('master_ingest')}
                onToggleFavorite={() => toggleFavorite("master_ingest")} 
                description="Connect to DaVinci Resolve, create/select project library, set working folders, import card footage, and build timelines."
                className="ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Auto Ingest" 
                icon={<FolderPlus size={18} />} 
                category="organize"
                helpText="Launches DaVinci Resolve, connects to the project library inside your Master Folder, creates a versioned project, configures working folders, builds Media Pool bins, and generates card timelines."
              >
                <div className="flex flex-col gap-4">
                  <div className="flex flex-col md:flex-row gap-3 items-end">
                    <div className="flex-1 w-full">
                      <InputField 
                        id="masterFolderInput" 
                        browseType="folder" 
                        placeholder="/Users/audiovisual/Desktop/2026-07-23_UNICEF_WASH_Visit" 
                      />
                    </div>
                    <div className="w-full md:w-1/3">
                      <ActionButton 
                        text="Start Auto Ingest" 
                        category="organize" variant="primary"
                        isLoading={loading['master_ingest']}
                        onClick={() => {
                          const inputEl = document.getElementById('masterFolderInput') as HTMLInputElement;
                          const folderPath = inputEl?.value?.trim();
                          if (!folderPath) {
                            addLog('Please select or enter a Master Folder path.', 'error');
                            return;
                          }
                          runTask('master_ingest', { master_folder_path: folderPath }, 'master_ingest');
                        }}
                      />
                    </div>
                  </div>
                  <div className="p-4 bg-black/40 rounded-xl border border-white/5 text-xs text-white/60 space-y-2 leading-relaxed">
                    <p className="font-semibold text-white/80">✨ How Auto Ingest Works with DaVinci Resolve:</p>
                    <p>• Automatically launches or connects to DaVinci Resolve.</p>
                    <p>• Selects/switches to the Project Library inside <code className="text-brand-primary">Davinci Resolve Database</code> (if present).</p>
                    <p>• Creates a versioned project named after the Master Folder (e.g. <code className="text-brand-primary">ProjectName_v2</code>).</p>
                    <p>• Automatically configures <code className="text-brand-primary">Project media location</code>, <code className="text-brand-primary">CacheClip</code>, and <code className="text-brand-primary">.gallery</code> to your Master Folder.</p>
                    <p>• Imports camera card footage into Media Pool Bins and generates individual Card Timelines inside the <code className="text-brand-primary">Projects</code> Bin.</p>
                  </div>
                </div>
              </FeatureCard>

            </div>
          )}

          {/* --- TAB: MAGIC TOOLS --- */}
          {(activeTab === 'magic' || activeTab === 'dashboard') && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('snapshot')} 
                id="snapshot"
                isFavorite={favorites.includes('snapshot')}
                onToggleFavorite={() => toggleFavorite("snapshot")} description="Saves a full backup of your current timeline before you run destructive tools."
                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Timeline Snapshot" 
                icon={<Camera size={18} />} 
                category="magic"
                helpText="Creates an instant backup copy of your current timeline before making any destructive changes. One-click undo insurance."
              >
                <div className="w-full md:w-1/3 mt-2">
                  <ActionButton 
                    text="Save Snapshot" 
                    category="magic" variant="primary"
                    isLoading={loading['snapshot']}
                      disabled={!context.current_timeline}
                      title={!context.current_timeline ? 'Requires an active timeline' : undefined}
                    onClick={() => runTask('snapshot', {}, 'snapshot')}
                  />
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('magic_bin_organizer')} 
                id="magic_bin_organizer"
                isFavorite={favorites.includes('magic_bin_organizer')}
                onToggleFavorite={() => toggleFavorite("magic_bin_organizer")} description="Sorts your Media Pool into video, audio, and image bins automatically."

                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Magic Bin Organizer" 
                icon={<FolderTree size={18} />} 
                category="organize"
                helpText="Scans the root Media Pool and automatically moves loose Video, Audio, and Image files into standard organized Bins."
              >
                <div className="w-full md:w-1/3 mt-2">
                  <ActionButton 
                    text="Organize Media Pool" 
                    category="organize" variant="primary"
                    isLoading={loading['magic_bins']}
                    onClick={() => runTask('organize_bins', {}, 'magic_bins')}
                  />
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('batch_clip_renamer')} 
                id="batch_clip_renamer"
                isFavorite={favorites.includes('batch_clip_renamer')}
                onToggleFavorite={() => toggleFavorite("batch_clip_renamer")} description="Renames every clip on Video Track 1 in sequence using your prefix." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."

                title="Batch Clip Renamer" 
                icon={<PenLine size={18} />} 
                category="destructive"
                helpText="Rename all clips on Video Track 1 with a sequential pattern. Enter a prefix like 'Interview' and clips become Interview_001, Interview_002, etc."
              >
                <InputField id="renamePrefix" placeholder="Name prefix (e.g. Interview)" />
                <div className="mt-4">
                  <ActionButton 
                    text="Rename All Clips"
                    isLoading={loading['rename']}
                    category="destructive" variant="primary" requiresConfirm onClick={() => runTask('batch_rename', {
                      prefix: (document.getElementById('renamePrefix') as HTMLInputElement).value,
                      start_number: 1,
                      scope: 'timeline'
                    }, 'rename')}
                  />
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('social_media_reframe')} 
                id="social_media_reframe"
                isFavorite={favorites.includes('social_media_reframe')}
                onToggleFavorite={() => toggleFavorite("social_media_reframe")} description="Reframes your timeline to 9:16 for Shorts or 1:1 for Square."

                title="Social Media Reframe" 
                icon={<Smartphone size={18} />} 
                category="output"
                helpText="Duplicates your current timeline and automatically sets the resolution to 9:16 or 1:1 with scale-to-crop settings."
              >
                <div className="flex flex-col gap-3">
                  <ActionButton 
                    text="Convert to 9:16 (Shorts/Reels)" 
                    category="output" variant="primary"
                    isLoading={loading['magic_reframe_916']}
                    onClick={() => runTask('social_reframe', { format: '9:16' }, 'magic_reframe_916')}
                  />
                  <ActionButton 
                    text="Convert to 1:1 (Square)" 
                    category="output" variant="secondary"
                    isLoading={loading['magic_reframe_11']}
                    onClick={() => runTask('social_reframe', { format: '1:1' }, 'magic_reframe_11')}
                  />
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('quick_title')} 
                id="quick_title"
                isFavorite={favorites.includes('quick_title')}
                onToggleFavorite={() => toggleFavorite("quick_title")} description="Drops a title card at the playhead."

                title="Quick Title" 
                icon={<Type size={18} />} 
                category="magic"
                helpText="Instantly adds a standard Text+ title at your current playhead position."
              >
                <ActionButton 
                  text="Add Title at Playhead" 
                  category="magic" variant="primary"
                  isLoading={loading['magic_title']}
                  onClick={() => runTask('add_title', {}, 'magic_title')}
                />
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('adjustment_layer')} 
                id="adjustment_layer"
                isFavorite={favorites.includes('adjustment_layer')}
                onToggleFavorite={() => toggleFavorite("adjustment_layer")} description="Drops an Adjustment Clip on Track 5 at playhead."
                title="Quick Adjustment Layer" 
                icon={<Combine size={18} />} 
                category="magic"
                helpText="Instantly adds an Adjustment Layer to Video Track 5 at your current playhead position without shifting clips. Requires an 'Adjustment Clip' in your Media Pool."
              >
                <ActionButton 
                  text="Add Adjustment Layer" 
                  category="magic" variant="primary"
                  isLoading={loading['magic_adj']}
                  disabled={!context.current_timeline}
                  title={!context.current_timeline ? 'Requires an active timeline' : undefined}
                  onClick={() => runTask('add_adjustment_layer', {}, 'magic_adj')}
                />
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('multicam_auto_sync')} 
                id="multicam_auto_sync"
                isFavorite={favorites.includes('multicam_auto_sync')}
                onToggleFavorite={() => toggleFavorite("multicam_auto_sync")} description="Syncs the clips you've selected using their audio waveforms."

                title="Multi-Cam Auto Sync" 
                icon={<Link size={18} />} 
                category="organize"
                helpText="Select at least one video and one audio clip in the Media Pool, then click this to auto-sync them by waveform."
              >
                <ActionButton 
                  text="Sync Selected Clips" 
                  category="organize" variant="primary"
                  isLoading={loading['magic_sync']}
                  onClick={() => runTask('auto_sync', {}, 'magic_sync')}
                />
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('badwords')} 
                id="badwords"
                isFavorite={favorites.includes('badwords')}
                onToggleFavorite={() => toggleFavorite("badwords")} description="Scans your timeline markers for flagged words and lists them for review." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."
                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="BadWords Cleaner" 
                icon={<Wand2 size={18} />} 
                category="destructive"
                helpText="Scans BadWords-generated color markers from the current timeline. Select which marker colors to remove, then create a clean timeline without those segments."
              >
                <div className="flex flex-col gap-4">
                  {/* Scan Button */}
                  <div className="flex items-center gap-3">
                    <div className="w-full md:w-1/3">
                      <ActionButton 
                        text="Scan Markers" 
                        category="destructive" variant="secondary"
                        isLoading={loading['bw_scan']}
                        onClick={async () => {
                          setLoading(prev => ({ ...prev, bw_scan: true }))
                          try {
                            const res = await fetch(`${API_BASE}/badwords/scan`)
                            const data = await res.json()
                            setBwScan(data)
                            if (data.success) {
                              addLog(`Found ${data.total_markers} markers on '${data.timeline_name}'`, 'success')
                            } else {
                              addLog(data.message, 'error')
                            }
                          } catch { addLog('Failed to scan markers', 'error') }
                          finally { setLoading(prev => ({ ...prev, bw_scan: false })) }
                        }}
                      />
                    </div>
                    {bwScan?.success && (
                      <p className="text-xs text-white/50">
                        Found <strong className="text-white/80">{bwScan.total_markers}</strong> markers · 
                        <strong className="text-white/80"> {bwScan.total_marked_seconds}s</strong> marked
                      </p>
                    )}
                  </div>

                  {/* Scan Results */}
                  {bwScan?.success && (
                    <div className="space-y-3">
                      {/* Color Summary Chips */}
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(bwScan.summary as Record<string, {count: number, total_seconds: number}>).map(([color, data]) => {
                          const colorMap: Record<string, string> = {
                            Red: 'bg-red-500/20 border-red-500/40 text-red-300',
                            Blue: 'bg-blue-500/20 border-blue-500/40 text-blue-300',
                            Green: 'bg-green-500/20 border-green-500/40 text-green-300',
                            Yellow: 'bg-yellow-500/20 border-yellow-500/40 text-yellow-300',
                            Purple: 'bg-purple-500/20 border-purple-500/40 text-purple-300',
                            Cyan: 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300',
                          }
                          const chipClass = colorMap[color] || 'bg-white/10 border-white/20 text-white/70'
                          return (
                            <span key={color} className={`px-3 py-1.5 rounded-lg border text-xs font-medium ${chipClass}`}>
                              {color}: {data.count} ({data.total_seconds}s)
                            </span>
                          )
                        })}
                      </div>

                      {/* Color Checkboxes */}
                      <div className="flex flex-wrap gap-4 px-1">
                        {['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Cyan'].filter(c => bwScan.summary[c]).map(color => (
                          <label key={color} className="flex items-center gap-2 cursor-pointer text-white/70 hover:text-white transition-colors text-xs">
                            <input 
                              type="checkbox" 
                              checked={bwColors[color] || false}
                              onChange={(e) => setBwColors(prev => ({ ...prev, [color]: e.target.checked }))}
                              className="w-3.5 h-3.5 accent-orange-500"
                            />
                            Remove {color}
                          </label>
                        ))}
                      </div>

                      {/* Clean Button */}
                      <div className="w-full md:w-1/3">
                        <ActionButton 
                          text="Clean Timeline" 
                          category="destructive" variant="primary" requiresConfirm
                          isLoading={loading['bw_clean']}
                          onClick={() => {
                            const selectedColors = Object.entries(bwColors)
                              .filter(([_, checked]) => checked)
                              .map(([color]) => color)
                            if (selectedColors.length === 0) {
                              addLog('No colors selected for removal', 'error')
                              return
                            }
                            runTask('badwords/clean', { colors: selectedColors }, 'bw_clean')
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </FeatureCard>
            </div>
          )}

          {/* --- TAB 1: CUT & EXTRACT --- */}
          {(activeTab === 'cut' || activeTab === 'dashboard') && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
              
              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('timecode_cutter')} 
                id="timecode_cutter"
                isFavorite={favorites.includes('timecode_cutter')}
                onToggleFavorite={() => toggleFavorite("timecode_cutter")} description="Slices your timeline at the timecodes, timestamps, or frame numbers you enter." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."

                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Timecode Cutter" 
                icon={<Scissors size={18} />} 
                category="destructive"
                helpText="Input timecode ranges to cut the timeline. 'Cut Inside' deletes the ranges and closes gaps. 'Cut Outside' keeps only the specified ranges."
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <textarea 
                    id="timecodes"
                    defaultValue={localStorage.getItem('timecodes') || ""}
                    onChange={(e) => localStorage.setItem('timecodes', e.target.value)}
                    className="w-full h-32 bg-black/40 border border-white/5 rounded-xl p-3 text-xs text-white/90 placeholder-white/20 focus:outline-none focus:border-brand-primary/50 transition-colors resize-none"
                    placeholder={"Supported Formats:\n01:00:00:00 - 01:00:05:00\n1m20s - 2m30s\n1500 - 2000 (Frames)\n\nExample:\n1m57-2m08\n3m10-3m22"}
                  />
                  <div className="flex flex-col gap-4 justify-between">
                    <InputField id="clipName" placeholder="Specific Target Clip Name (Optional)" />
                    <div className="flex gap-3 mt-auto">
                      <div className="flex-1">
                        <ActionButton 
                          text="Cut Inside Ranges" 
                          category="destructive" variant="primary" requiresConfirm
                          isLoading={loading['cut_in']}
                          onClick={() => runTask('cut', {
                            timecodes: (document.getElementById('timecodes') as HTMLTextAreaElement).value,
                            clip_name: (document.getElementById('clipName') as HTMLInputElement).value
                          }, 'cut_in')}
                        />
                      </div>
                      <div className="flex-1">
                        <ActionButton 
                          text="Cut Outside (Reverse)" 
                          category="destructive" variant="primary" requiresConfirm
                          isLoading={loading['cut_out']}
                          onClick={() => runTask('cut', {
                            timecodes: (document.getElementById('timecodes') as HTMLTextAreaElement).value,
                            clip_name: (document.getElementById('clipName') as HTMLInputElement).value,
                            reverse: true
                          }, 'cut_out')}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('clip_picker')} 
                id="clip_picker"
                isFavorite={favorites.includes('clip_picker')}
                onToggleFavorite={() => toggleFavorite("clip_picker")} description="Builds a new timeline from the specific clip numbers you list." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."
                title="Clip Picker" 
                icon={<Target size={18} />} 
                category="destructive"
                helpText="Enter clip names or numerical ranges (e.g., 8607-8610, 8804). The app will build a new timeline."
              >
                <InputField id="pickNames" placeholder="e.g. 8607-8610, 8804" />
                <div className="mt-4">
                  <ActionButton 
                    text="Build Timeline from Clips"
                    isLoading={loading['picker']}
                    category="destructive" variant="primary" requiresConfirm onClick={() => runTask('pick_clips', {names: (document.getElementById('pickNames') as HTMLInputElement).value}, 'picker')}
                  />
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('markers_to_timeline')} 
                id="markers_to_timeline"
                isFavorite={favorites.includes('markers_to_timeline')}
                onToggleFavorite={() => toggleFavorite("markers_to_timeline")} description="Extracts every clip marked with the selected color into a fresh timeline." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."

                title="Markers to Timeline" 
                icon={<MapPin size={18} />} 
                category="destructive"
                helpText="Select a marker color. All marked clips will be extracted into a new timeline."
              >
                <SelectField id="markerColor" options={['All', 'Blue', 'Cyan', 'Green', 'Yellow', 'Red', 'Pink', 'Purple', 'Fuchsia', 'Rose', 'Lavender', 'Sky', 'Mint', 'Lemon', 'Sand', 'Cocoa', 'Cream']} />
                <ActionButton 
                  text="Extract Marked Clips" 
                  category="neutral" variant="secondary"
                  isLoading={loading['markers']}
                  onClick={() => runTask('markers_to_timeline', {color: (document.getElementById('markerColor') as HTMLSelectElement).value}, 'markers')}
                />
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('flag_filter')} 
                id="flag_filter"
                isFavorite={favorites.includes('flag_filter')}
                onToggleFavorite={() => toggleFavorite("flag_filter")} description="Pulls only the clips flagged with the color you choose."

                title="Flag Filter" 
                icon={<Flag size={18} />} 
                category="organize"
                helpText="Select a flag color to copy flagged clips to a new timeline."
              >
                <SelectField id="flagColor" options={['Blue', 'Cyan', 'Green', 'Yellow', 'Red', 'Pink', 'Purple', 'Fuchsia', 'Rose', 'Lavender', 'Sky', 'Mint', 'Lemon', 'Sand', 'Cocoa', 'Cream']} />
                <ActionButton 
                  text="Extract Flagged Clips" 
                  category="organize" variant="secondary"
                  isLoading={loading['flags']}
                      disabled={!context.current_timeline}
                      title={!context.current_timeline ? 'Requires an active timeline' : undefined}
                  onClick={() => runTask('filter_by_flag', {color: (document.getElementById('flagColor') as HTMLSelectElement).value}, 'flags')}
                />
              </FeatureCard>
            </div>
          )}

          {/* --- TAB 2: MERGE & PROCESS --- */}
          {(activeTab === 'process' || activeTab === 'dashboard') && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
              
              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('merge_timelines')} 
                id="merge_timelines"
                isFavorite={favorites.includes('merge_timelines')}
                onToggleFavorite={() => toggleFavorite("merge_timelines")} description="Appends the timelines you select into one master timeline, in order." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."

                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Merge Timelines" 
                icon={<Combine size={18} />} 
                category="destructive"
                helpText="Click to select multiple timelines. They will be copied into a single Master Timeline."
              >
                <div className="flex flex-col gap-4">
                  <div className="flex justify-between items-center text-sm text-white/80">
                    <span>Select Timelines to Merge:</span>
                    {context.timelines.length > 0 && (
                      <div className="flex gap-3">
                        <button onClick={() => setSelectedMergeTimelines([...context.timelines])} className="text-xs text-brand-secondary hover:text-white transition-colors">Select All</button>
                        <button onClick={() => setSelectedMergeTimelines([])} className="text-xs text-brand-secondary hover:text-white transition-colors">Clear All</button>
                      </div>
                    )}
                  </div>
                  {context.timelines.length > 0 ? (
                    <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-2 custom-scrollbar border border-white/5 rounded-lg p-2 bg-black/20">
                      {context.timelines.map(t => (
                        <button
                          key={t}
                          onClick={() => setSelectedMergeTimelines(prev => prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t])}
                          className={`flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium transition-all text-left w-full ${selectedMergeTimelines.includes(t) ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-[0_0_15px_rgba(245,158,11,0.1)]' : 'bg-transparent text-white/60 hover:bg-white/5 border border-transparent'}`}
                        >
                          <div className={`w-3.5 h-3.5 rounded-sm border flex items-center justify-center transition-colors ${selectedMergeTimelines.includes(t) ? 'bg-amber-500 border-amber-500 text-black' : 'border-white/30'}`}>
                            {selectedMergeTimelines.includes(t) && <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                          </div>
                          <span className="truncate">{t}</span>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-white/30 italic p-3 bg-black/20 rounded-xl border border-white/5">No timelines found. Connect to a project first.</div>
                  )}
                  <div className="flex justify-end mt-2">
                    <div className="w-full md:w-1/3">
                      <ActionButton 
                        text={selectedMergeTimelines.length > 0 ? `Merge ${selectedMergeTimelines.length} Timelines` : "Merge Timelines"}
                        category="destructive" variant="primary" requiresConfirm
                        isLoading={loading['merge']}
                        onClick={() => {
                          if (selectedMergeTimelines.length < 1) {
                            addLog('Please select at least one timeline to merge', 'error');
                            return;
                          }
                          runTask('merge_timelines', {timeline_names: selectedMergeTimelines.join(',')}, 'merge')
                        }}
                      />
                    </div>
                  </div>
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('watermark_track')} 
                id="watermark_track"
                isFavorite={favorites.includes('watermark_track')}
                onToggleFavorite={() => toggleFavorite("watermark_track")} description="Places your logo across the top track of the whole video."

                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Watermark Track" 
                icon={<Droplet size={18} />} 
                category="output"
                helpText="Provide the path to an image to place it on a top video track."
              >
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <InputField id="watermarkPath" browseType="file" placeholder="/Users/name/Desktop/logo.png" />
                  </div>
                  <div className="w-full md:w-1/3">
                    <ActionButton 
                      text="Apply Watermark" 
                      category="output" variant="primary"
                      isLoading={loading['watermark']}
                      disabled={!context.current_timeline}
                      title={!context.current_timeline ? 'Requires an active timeline' : undefined}
                      onClick={() => runTask('apply_watermark', {image_path: (document.getElementById('watermarkPath') as HTMLInputElement).value}, 'watermark')}
                    />
                  </div>
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('auto_jcut__lcut')} 
                id="auto_jcut__lcut"
                isFavorite={favorites.includes('auto_jcut__lcut')}
                onToggleFavorite={() => toggleFavorite("auto_jcut__lcut")} description="Offsets audio at each cut point to smooth interview edits." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."

                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Auto J-Cut / L-Cut" 
                icon={<AudioLines size={18} />} 
                category="destructive"
                helpText="Automatically offset audio at every edit point for smoother transitions. J-Cut: next audio starts early. L-Cut: current audio extends."
              >
                <div className="flex flex-col md:flex-row gap-5 items-end">
                  <div className="flex-1 w-full flex flex-col md:flex-row gap-4">
                    <div className="w-full md:w-1/2">
                      <SelectField id="jlType" options={['J-Cut (Audio First)', 'L-Cut (Audio Extends)']} />
                    </div>
                    <div className="w-full md:w-1/2">
                      <InputField id="jlOverlap" placeholder="Overlap frames (default: 10)" />
                    </div>
                  </div>
                  <div className="w-full md:w-1/3">
                    <ActionButton 
                      text="Apply Cuts"
                      isLoading={loading['jlcut']}
                      disabled={!context.current_timeline}
                      title={!context.current_timeline ? 'Requires an active timeline' : undefined}
                      category="destructive" variant="primary" requiresConfirm onClick={() => {
                        const typeVal = (document.getElementById('jlType') as HTMLSelectElement).value
                        const cutType = typeVal.startsWith('J') ? 'j' : 'l'
                        const overlap = parseInt((document.getElementById('jlOverlap') as HTMLInputElement).value) || 10
                        runTask('jl_cut', { cut_type: cutType, overlap_frames: overlap }, 'jlcut')
                      }}
                    />
                  </div>
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('silence_remover')} 
                id="silence_remover"
                isFavorite={favorites.includes('silence_remover')}
                onToggleFavorite={() => toggleFavorite("silence_remover")} description="Detects dead air on Track 1 and ripple-deletes it automatically." warning="This modifies your timeline directly. Use Timeline Snapshot first if unsure."

                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Silence Remover" 
                icon={<VolumeX size={18} />} 
                category="destructive"
                helpText="Detects silent sections in the audio and creates a new timeline without them. Perfect for jump-cut style content. Requires pydub + ffmpeg."
              >
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 flex gap-3">
                    <InputField id="silenceDb" placeholder="Threshold dB (-40)" />
                    <InputField id="silenceMin" placeholder="Min silence ms (500)" />
                    <InputField id="silencePad" placeholder="Padding ms (100)" />
                  </div>
                  <div className="w-full md:w-1/3">
                    <ActionButton 
                      text="Remove Silence"
                      isLoading={loading['silence']}
                      disabled={!context.current_timeline}
                      title={!context.current_timeline ? 'Requires an active timeline' : undefined}
                      category="destructive" variant="primary" requiresConfirm onClick={() => {
                        const db = parseInt((document.getElementById('silenceDb') as HTMLInputElement).value) || -40
                        const minMs = parseInt((document.getElementById('silenceMin') as HTMLInputElement).value) || 500
                        const padMs = parseInt((document.getElementById('silencePad') as HTMLInputElement).value) || 100
                        runTask('silence_remove', { threshold_db: db, min_silence_ms: minMs, padding_ms: padMs }, 'silence')
                      }}
                    />
                  </div>
                </div>
              </FeatureCard>
            </div>
          )}

          {/* --- TAB 3: EXPORT & DATA --- */}
          {(activeTab === 'export' || activeTab === 'dashboard') && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
              
              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('multiplatform_render')} 
                id="multiplatform_render"
                isFavorite={favorites.includes('multiplatform_render')}
                onToggleFavorite={() => toggleFavorite("multiplatform_render")} description="Batch render multiple timelines with your chosen preset."
                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Batch Timeline Render" 
                icon={<MonitorUp size={18} />} 
                category="render"
                helpText="Adds render jobs to the Render Queue for selected timelines using a Resolve Preset."
              >
                <div className="flex flex-col gap-4 mb-4">
                  <div className="flex justify-between items-center text-sm text-white/80">
                    <span>Select Timelines to Render:</span>
                    {context.timelines.length > 0 && (
                      <div className="flex gap-3">
                        <button onClick={() => setSelectedBatchTimelines([...context.timelines])} className="text-xs text-brand-secondary hover:text-white transition-colors">Select All</button>
                        <button onClick={() => setSelectedBatchTimelines([])} className="text-xs text-brand-secondary hover:text-white transition-colors">Clear All</button>
                      </div>
                    )}
                  </div>
                  {context.timelines.length > 0 ? (
                    <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-2 custom-scrollbar border border-white/5 rounded-lg p-2 bg-black/20">
                      {context.timelines.map(name => (
                        <button 
                          key={name}
                          onClick={() => setSelectedBatchTimelines(prev => prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name])}
                          className={`flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium transition-all text-left w-full ${selectedBatchTimelines.includes(name) ? 'bg-brand-primary/20 text-brand-primary border border-brand-primary/30' : 'bg-transparent text-white/60 hover:bg-white/5 border border-transparent'}`}
                        >
                          <div className={`w-3.5 h-3.5 rounded-sm border flex items-center justify-center transition-colors ${selectedBatchTimelines.includes(name) ? 'bg-brand-primary border-brand-primary text-black' : 'border-white/30'}`}>
                            {selectedBatchTimelines.includes(name) && <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                          </div>
                          <span className="truncate">{name}</span>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-brand-warning/80 italic bg-brand-warning/10 p-2 rounded border border-brand-warning/20">No timelines found in project.</div>
                  )}
                </div>
                
                <div className="flex flex-col md:flex-row gap-5 items-end">
                  <div className="flex-1 space-y-4">
                    <div>
                      <div className="text-xs text-white/60 mb-1 flex justify-between items-center">
                        <span>Resolve Preset Name:</span>
                        <button 
                          onClick={() => fetch(`${API_BASE}/open_folder?path=presets`)}
                          className="text-brand-secondary hover:text-brand-secondary/80 hover:underline"
                        >
                          Locate Bundled XML
                        </button>
                      </div>
                      <input 
                        type="text" 
                        id="renderPresetName" 
                        defaultValue="ClipAssassin Render_MP4_H.264_with Subtitle" 
                        className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/90 focus:outline-none focus:border-brand-primary/50 transition-colors"
                        placeholder="e.g. Custom Export"
                      />
                    </div>
                    <InputField id="renderDir" browseType="folder" placeholder="Output Directory Path" />
                  </div>
                  <div className="w-full md:w-1/3">
                    <ActionButton 
                      text="Add to Render Queue" 
                      category="render" variant="primary"
                      isLoading={loading['render']}
                      disabled={selectedBatchTimelines.length === 0}
                      title={selectedBatchTimelines.length === 0 ? 'Select at least one timeline' : undefined}
                      onClick={() => {
                        runTask('batch_render', {
                          timelines: selectedBatchTimelines, 
                          preset_name: (document.getElementById('renderPresetName') as HTMLInputElement).value,
                          target_dir: (document.getElementById('renderDir') as HTMLInputElement).value
                        }, 'render')
                      }}
                    />
                  </div>
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('extract_thumbnails')} 
                id="extract_thumbnails"
                isFavorite={favorites.includes('extract_thumbnails')}
                onToggleFavorite={() => toggleFavorite("extract_thumbnails")} description="Saves a still frame at every marker (or selection) to your chosen folder."

                title="Extract Thumbnails" 
                icon={<ImageIcon size={18} />} 
                category="output"
                helpText="'Markers' mode exports a still frame at every timeline marker."
              >
                <SelectField id="thumbMode" options={['Markers', 'Timeline Center']} />
                <div className="mb-4">
                  <InputField id="thumbDir" browseType="folder" placeholder="Save directory" />
                </div>
                <ActionButton 
                  text="Export Still Frames" 
                  category="output" variant="primary"
                  isLoading={loading['thumb']}
                  onClick={() => runTask('extract_thumbnails', {mode: (document.getElementById('thumbMode') as HTMLSelectElement).value, target_dir: (document.getElementById('thumbDir') as HTMLInputElement).value}, 'thumb')}
                />
              </FeatureCard>


              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('auto_youtube_chapters')} 
                id="auto_youtube_chapters"
                isFavorite={favorites.includes('auto_youtube_chapters')}
                onToggleFavorite={() => toggleFavorite("auto_youtube_chapters")} description="Generates timestamped chapters from your timeline markers."

                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Auto YouTube Chapters" 
                icon={<Video size={18} />} 
                category="render"
                helpText="Generates a YouTube timestamp list from timeline markers."
              >
                <div className="w-full md:w-1/3">
                  <ActionButton 
                    text="Generate Chapters" 
                    category="render" variant="primary"
                    isLoading={loading['yt']}
                    onClick={() => runTask('youtube_chapters', {}, 'yt')}
                  />
                </div>
              </FeatureCard>

              <FeatureCard hidden={activeTab === 'dashboard' && !favorites.includes('shotlist_generator')} 
                id="shotlist_generator"
                isFavorite={favorites.includes('shotlist_generator')}
                onToggleFavorite={() => toggleFavorite("shotlist_generator")} description="Exports your clip list as a CSV for client review."
                className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
                title="Client Shotlist / Document Exporter" 
                icon={<FileSpreadsheet size={18} />} 
                category="output"
                helpText="Exports a professional shotlist of Video Track 1. Choose CSV or Word (.docx) template."
              >
                <div className="flex flex-col gap-3">
                  <div className="flex gap-3">
                    <select 
                      className="bg-black/40 border border-white/5 rounded-xl px-4 py-3 text-xs text-white/90 focus:outline-none appearance-none cursor-pointer w-1/3"
                      value={shotlistFormat}
                      onChange={(e) => setShotlistFormat(e.target.value)}
                    >
                      <option value="csv" className="bg-[#111]">CSV Spreadsheet</option>
                      <option value="docx" className="bg-[#111]">Word Document (.docx)</option>
                    </select>
                    
                    <div className="flex-1">
                      <InputField 
                        id="shotlistPath" 
                        browseType="folder" 
                        placeholder="C:\Exports" 
                      />
                    </div>
                  </div>
                  
                  {shotlistFormat === 'docx' && (
                    <InputField id="shotlistTemplate" browseType="file" placeholder="C:\Templates\shotlist_template.docx" />
                  )}
                  
                  <div className="w-full md:w-1/3 mt-2">
                    <ActionButton 
                      text={`Export ${shotlistFormat === 'docx' ? 'Word Document' : 'CSV'}`}
                      category="output" variant="primary"
                      isLoading={loading['shotlist']}
                      disabled={!context.current_timeline}
                      title={!context.current_timeline ? 'Requires an active timeline' : undefined}
                      onClick={() => runTask('export_shotlist', {
                        format: shotlistFormat,
                        target_path: (document.getElementById('shotlistPath') as HTMLInputElement).value,
                        template_path: shotlistFormat === 'docx' ? (document.getElementById('shotlistTemplate') as HTMLInputElement).value : ""
                      }, 'shotlist')}
                    />
                  </div>
                </div>
              </FeatureCard>
            </div>
          )}

          {/* --- TAB: SETTINGS --- */}
          {activeTab === 'settings' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-5 mb-5">
              
              <div className="bg-black/20 backdrop-blur-3xl border border-white/5 rounded-[20px] p-6 shadow-2xl">
                 <h3 className="text-sm font-semibold mb-4 text-white/80 uppercase tracking-wider flex items-center gap-2">
                    <Sparkles size={16} className="text-brand-primary" /> App Customization
                 </h3>
                 <div className="flex gap-4">
                    {themes.map(t => (
                      <button 
                        key={t.name}
                        onClick={() => applyTheme(t)}
                        className={`w-8 h-8 rounded-full border-2 transition-all hover:scale-110 ${localStorage.getItem('appTheme') === t.name ? 'border-white' : 'border-transparent'}`}
                        style={{ backgroundColor: t.primary }}
                        title={t.name}
                      />
                    ))}
                 </div>
                 <p className="text-xs text-white/40 mt-4">Select a theme color. It will automatically save and persist across sessions.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="bg-black/20 backdrop-blur-3xl border border-white/5 rounded-[20px] p-6 shadow-2xl">
                  <h3 className="text-sm font-semibold mb-4 text-white/80 uppercase tracking-wider flex items-center gap-2">
                    <MonitorUp size={16} className="text-brand-primary" /> App Preferences
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-white/90">Background Animations</p>
                        <p className="text-xs text-white/40 mt-0.5">Toggle animated glowing orbs</p>
                      </div>
                      <button 
                        onClick={() => setAnimationsEnabled(!animationsEnabled)}
                        className={`w-12 h-6 rounded-full transition-colors relative ${animationsEnabled ? 'bg-brand-primary' : 'bg-white/10'}`}
                      >
                        <div className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-all ${animationsEnabled ? 'left-7' : 'left-1'}`} />
                      </button>
                    </div>
                    <div className="pt-4 border-t border-white/5">
                      <ActionButton 
                        text="Clear Mission Log"
                        variant="secondary"
                        onClick={() => setLogs([])}
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-black/20 backdrop-blur-3xl border border-rose-500/20 rounded-[20px] p-6 shadow-2xl">
                  <h3 className="text-sm font-semibold mb-4 text-rose-400 uppercase tracking-wider flex items-center gap-2">
                    <Activity size={16} /> Danger Zone
                  </h3>
                  <div className="space-y-3">
                    <p className="text-xs text-white/40 mb-2">Reset the application if you encounter bugs or want a fresh start.</p>
                    <ActionButton 
                      text="Reset Dashboard Defaults"
                      variant="secondary"
                      onClick={() => {
                        setFavorites([])
                        addLog('Dashboard reset to defaults', 'info')
                      }}
                    />
                    <ActionButton 
                      text="Factory Reset App"
                      variant="secondary"
                      onClick={() => {
                        localStorage.clear()
                        window.location.reload()
                      }}
                    />
                  </div>
                </div>
              </div>

            </div>
          )}

          {/* --- PROJECT STATS DASHBOARD (Shows on Dashboard) --- */}
          {activeTab === 'dashboard' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 grid grid-cols-1 md:grid-cols-2 gap-5 items-start mb-5">
              <div className="bg-black/20 backdrop-blur-3xl border border-white/5 rounded-[20px] p-6 shadow-2xl md:col-span-2">
                <h3 className="text-sm font-semibold mb-4 text-white/80 uppercase tracking-wider flex items-center gap-2">
                  <BarChart3 size={16} className="text-brand-primary" /> Project Stats Dashboard
                </h3>
                <div className="mb-4">
                  <ActionButton 
                    text="Refresh Stats" 
                    category="neutral" variant="secondary"
                    isLoading={loading['proj_stats']}
                    onClick={async () => {
                      setLoading(prev => ({ ...prev, proj_stats: true }))
                      try {
                        const res = await fetch(`${API_BASE}/project_stats`)
                        const data = await res.json()
                        setProjectStats(data)
                        if (data.success) addLog(`Loaded stats for ${data.project_name}`, 'success')
                      } catch { addLog('Failed to get project stats', 'error') }
                      finally { setLoading(prev => ({ ...prev, proj_stats: false })) }
                    }}
                  />
                </div>
                {projectStats?.success ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-black/40 p-4 rounded-xl border border-white/5">
                      <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1">Total Timelines</p>
                      <p className="text-2xl font-semibold text-white/90">{projectStats.timeline_count}</p>
                    </div>
                    <div className="bg-black/40 p-4 rounded-xl border border-white/5">
                      <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1">Total Duration</p>
                      <p className="text-2xl font-semibold text-white/90">{projectStats.total_duration_seconds}s</p>
                    </div>
                    <div className="bg-black/40 p-4 rounded-xl border border-white/5">
                      <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1">Used Clips</p>
                      <p className="text-2xl font-semibold text-white/90">{projectStats.total_clips_used}</p>
                    </div>
                    <div className="bg-black/40 p-4 rounded-xl border border-white/5">
                      <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1">Media Pool Files</p>
                      <p className="text-2xl font-semibold text-white/90">{projectStats.total_pool_clips}</p>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-white/30 italic">Click refresh to load project statistics.</p>
                )}
              </div>
            </div>
          )}

          {/* --- DEVELOPER CONTACT --- */}
          {activeTab === 'settings' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
              <div className="bg-black/20 backdrop-blur-3xl border border-white/5 rounded-[20px] p-6 shadow-2xl md:col-span-2">
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-sm font-semibold mb-3 text-white/80 uppercase tracking-wider">Developer Contact</h3>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3 p-3 rounded-xl bg-black/20 border border-white/5">
                        <User size={16} className="text-brand-primary/70" />
                        <div>
                          <p className="text-[10px] text-white/40 uppercase tracking-wider">Creator</p>
                          <p className="font-medium text-white/80 text-xs">Zabid Al Muttaki</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-xl bg-black/20 border border-white/5">
                        <Mail size={16} className="text-brand-primary/70" />
                        <div>
                          <p className="text-[10px] text-white/40 uppercase tracking-wider">Email</p>
                          <p className="font-medium text-white/80 text-xs">zabid.coder@gmail.com</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                     <h3 className="text-sm font-semibold mb-3 text-white/80 uppercase tracking-wider">About Clip Assassin</h3>
                     <p className="text-xs text-white/50 leading-relaxed mb-3">Clip Assassin is an advanced automation suite tailored specifically for DaVinci Resolve. Built to dramatically reduce repetitive tasks in professional post-production workflows.</p>
                     <p className="text-[10px] font-mono text-brand-primary bg-brand-primary/10 px-2 py-1 rounded inline-block">Version 2.0.1</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* --- TAB: USER MANUAL --- */}
          {activeTab === 'manual' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
              
              <div className="mb-2">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <BookOpen className="text-brand-primary" /> User Manual
                </h2>
                <p className="text-xs text-white/50 mt-1">Step-by-step documentation for all Clip Assassin tools.</p>
              </div>

              <div className="space-y-4">
                <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Activity size={16}/> Dashboard & Basics</h3>
                  <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
                    <li><strong>Global Selection:</strong> Use the top-left dropdown to instantly switch your active timeline in Resolve.</li>
                    <li><strong>Keyboard Shortcuts:</strong> Press <code>Cmd+1</code> to <code>6</code> to switch tabs. Press <code>Cmd+R</code> to reconnect.</li>
                    <li><strong>Smart Presets:</strong> The app automatically saves your render paths and dropdown selections locally.</li>
                    <li><strong>Undo:</strong> If you make a mistake, simply press <code>Ctrl+Z</code> inside DaVinci Resolve to undo any automated action.</li>
                    <li><strong>Pin to Dashboard:</strong> Click the Pin icon on any tool card across the app to pin it to your Dashboard for quick access.</li>
                  </ul>
                </div>

                <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-brand-primary font-semibold mb-3 flex items-center gap-2"><FolderPlus size={16}/> Master Ingest & Folder Template Reference</h3>
                  <div className="text-sm text-white/70 space-y-3">
                    <p><strong>1. Master Folder Setup:</strong> Creates date-prefixed folders (<code>YYYY-MM-DD_[Client]_[Project]</code>) on disk with standard sub-folder templates.</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs bg-black/40 p-4 rounded-xl border border-white/5 leading-relaxed font-mono">
                      <div>
                        <span className="text-brand-primary font-bold block mb-1">Standard Video & Film</span>
                        • Raw Footages/Card 01<br/>
                        • Raw Footages/Card 02<br/>
                        • Davinci Resolve Database<br/>
                        • Logos & Branding<br/>
                        • BG Music<br/>
                        • After Effects / Photoshop<br/>
                        • Exports & Documents
                      </div>
                      <div>
                        <span className="text-cyan-400 font-bold block mb-1">Social Media & Reels</span>
                        • Raw Footages/Card 01<br/>
                        • Davinci Resolve Database<br/>
                        • Logos & Branding<br/>
                        • Audio & Music<br/>
                        • Graphics & Assets<br/>
                        • Exports
                      </div>
                      <div>
                        <span className="text-emerald-400 font-bold block mb-1">Commercial / Corporate</span>
                        • Raw Footages/Camera A & B<br/>
                        • Davinci Resolve Database<br/>
                        • Logos & Branding<br/>
                        • Audio & Voiceover<br/>
                        • Motion Graphics<br/>
                        • Client Approvals & Exports
                      </div>
                    </div>
                    <p><strong>2. Auto Ingest Workflow:</strong> Launches DaVinci Resolve, connects to the Project Library inside <code>Davinci Resolve Database</code>, creates a versioned project, configures working folders (Project Media Location, CacheClip, .gallery), imports camera footage into Media Pool Bins, and builds individual Card Timelines inside the <code>Projects</code> bin.</p>
                  </div>
                </div>

                <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Sparkles size={16}/> Magic Tools</h3>
                  <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
                    <li><strong>Timeline Snapshot:</strong> Saves a full backup of your current timeline before you run destructive tools.</li>
                    <li><strong>Magic Bin Organizer:</strong> Sorts your Media Pool into video, audio, and image bins automatically.</li>
                    <li><strong>Batch Clip Renamer:</strong> Renames every clip on Video Track 1 in sequence using your prefix.</li>
                    <li><strong>Social Media Reframe:</strong> Reframes your timeline to 9:16 for Shorts or 1:1 for Square.</li>
                    <li><strong>Quick Title:</strong> Drops a title card at the playhead.</li>
                    <li><strong>Quick Adjustment Layer:</strong> Drops an adjustment clip on Track 5 at the playhead (requires Media Pool).</li>
                    <li><strong>Multi-Cam Auto Sync:</strong> Syncs the clips you've selected using their audio waveforms.</li>
                    <li><strong>BadWords Cleaner:</strong> Scans your timeline markers for flagged words and lists them for review.</li>
                  </ul>
                </div>

                <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Scissors size={16}/> Cut & Trim Tools</h3>
                  <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
                    <li><strong>Timecode Cutter:</strong> Slices your timeline at the timecodes, timestamps, or frame numbers you enter.</li>
                    <li><strong>Clip Picker:</strong> Builds a new timeline from the specific clip numbers you list.</li>
                    <li><strong>Markers to Timeline:</strong> Extracts every clip marked with the selected color into a fresh timeline.</li>
                    <li><strong>Flag Filter:</strong> Pulls only the clips flagged with the color you choose.</li>
                  </ul>
                </div>

                <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Combine size={16}/> Process Tools</h3>
                  <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
                    <li><strong>Merge Timelines:</strong> Appends the timelines you select into one master timeline, in order.</li>
                    <li><strong>Watermark Track:</strong> Places your logo across the top track of the whole video.</li>
                    <li><strong>Auto J-Cut / L-Cut:</strong> Offsets audio at each cut point to smooth interview edits.</li>
                    <li><strong>Silence Remover:</strong> Detects dead air on Track 1 and ripple-deletes it automatically.</li>
                  </ul>
                </div>

                <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><MonitorUp size={16}/> Export Tools</h3>
                  <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
                    <li><strong>Batch Timeline Render:</strong> Batch renders multiple selected timelines using a custom DaVinci Resolve preset.</li>
                    <li><strong>Extract Thumbnails:</strong> Saves a still frame at every marker (or selection) to your chosen folder.</li>
                    <li><strong>Auto YouTube Chapters:</strong> Generates timestamped chapters from your timeline markers.</li>
                    <li><strong>Client Shotlist / Document Exporter:</strong> Exports your clip list as a CSV for client review.</li>
                  </ul>
                </div>

                <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Library size={16}/> Templates</h3>
                  <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
                    <li><strong>Asset Library:</strong> Imports .drfx templates from your plugin folder straight into the Media Pool.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
          
        </div>
      </div>

      {/* Toasts */}
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
          { id: 'batch_timeline_render', title: 'Batch Timeline Render', icon: <MonitorUp size={16} />, perform: () => setActiveTab('render') },
          { id: 'auto_youtube_chapters', title: 'Auto YouTube Chapters', icon: <Video size={16} />, perform: () => runTask('youtube_chapters', {}, 'chapters') },
          { id: 'shotlist_generator', title: 'Client Shotlist / Document Exporter', icon: <FileSpreadsheet size={16} />, keywords: ['csv', 'excel', 'doc', 'word'], perform: () => setActiveTab('export') },
        ]}
      />

      {/* Bottom Right App Badge */}
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
