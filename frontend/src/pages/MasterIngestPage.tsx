import { FolderTree, FolderPlus } from 'lucide-react'
import { ActionButton, FeatureCard, InputField, SelectField } from '../components/ui'

interface Props {
  isDashboard: boolean
  favorites: string[]
  toggleFavorite: (id: string) => void
  loading: Record<string, boolean>
  handleCreateMasterFolder: () => void
  addLog: (msg: string, type: 'info' | 'success' | 'error') => void
  runTask: (endpoint: string, payload: any, buttonId: string) => void
}

export function MasterIngestPage({ isDashboard, favorites, toggleFavorite, loading, handleCreateMasterFolder, addLog, runTask }: Props) {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6 mb-6">
      <FeatureCard hidden={isDashboard && !favorites.includes('create_master_folder')}
        id="create_master_folder"
        isFavorite={favorites.includes('create_master_folder')}
        onToggleFavorite={() => toggleFavorite('create_master_folder')}
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
              <InputField id="createParentFolderInput" browseType="folder" placeholder="/Users/audiovisual/Desktop" />
            </div>
            <div>
              <label className="text-xs font-semibold text-white/70 mb-1.5 block">Project Name *</label>
              <InputField id="createProjectNameInput" placeholder="e.g. UNICEF_WASH_Visit" />
            </div>
            <div>
              <label className="text-xs font-semibold text-white/70 mb-1.5 block">Project Date (YYYY-MM-DD)</label>
              <InputField id="createDateInput" type="date" placeholder="YYYY-MM-DD" defaultValue={new Date().toISOString().split('T')[0]} />
            </div>
            <div>
              <label className="text-xs font-semibold text-white/70 mb-1.5 block">Client / Agency (Optional)</label>
              <InputField id="createClientNameInput" placeholder="e.g. UNICEF" />
            </div>
            <div className="md:col-span-2">
              <label className="text-xs font-semibold text-white/70 mb-1.5 block">Folder Template Preset</label>
              <SelectField id="createPresetSelect" options={['Standard Video & Film', 'Social Media & Reels', 'Commercial / Corporate']} />
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

      <FeatureCard hidden={isDashboard && !favorites.includes('master_ingest')}
        id="master_ingest"
        isFavorite={favorites.includes('master_ingest')}
        onToggleFavorite={() => toggleFavorite('master_ingest')}
        description="Automate project creation, working folder paths, Media Pool bins, and card timelines in DaVinci Resolve."
        className="ring-1 ring-brand-primary/30 shadow-xl shadow-brand-primary/20"
        title="Auto Ingest"
        icon={<FolderPlus size={18} />}
        category="organize"
        helpText="Open DaVinci Resolve with your desired Project Library active. Clip Assassin will create a versioned project, configure working folders to your Master Folder, build Media Pool card bins, import footage, and generate timelines."
      >
        <div className="flex flex-col gap-4">
          <div className="flex flex-col md:flex-row gap-3 items-end">
            <div className="flex-1 w-full">
              <InputField id="masterFolderInput" browseType="folder" placeholder="/Users/audiovisual/Desktop/2026-07-23_UNICEF_WASH_Visit" />
            </div>
            <div className="w-full md:w-1/3">
              <ActionButton
                text="Start Auto Ingest"
                category="organize" variant="primary"
                isLoading={loading['master_ingest']}
                onClick={() => {
                  const inputEl = document.getElementById('masterFolderInput') as HTMLInputElement
                  const folderPath = inputEl?.value?.trim()
                  if (!folderPath) {
                    addLog('Please select or enter a Master Folder path.', 'error')
                    return
                  }
                  runTask('master_ingest', { master_folder_path: folderPath }, 'master_ingest')
                }}
              />
            </div>
          </div>
          <div className="p-4 bg-black/40 rounded-xl border border-white/5 text-xs text-white/60 space-y-2 leading-relaxed">
            <p className="font-semibold text-white/80">How Auto Ingest works:</p>
            <p>Connects to your active DaVinci Resolve session (open Resolve with your Project Library selected).</p>
            <p>Creates a versioned project named after the Master Folder (e.g. <code className="text-brand-primary">ProjectName_v2</code>).</p>
            <p>Automatically configures <code className="text-brand-primary">Project media location</code>, <code className="text-brand-primary">CacheClip</code>, and <code className="text-brand-primary">.gallery</code> working folders to your Master Folder.</p>
            <p>Imports camera card footage into Media Pool Bins mirroring card sub-folders.</p>
            <p>Generates individual Card Timelines inside the <code className="text-brand-primary">Projects</code> Bin automatically.</p>
          </div>
        </div>
      </FeatureCard>
    </div>
  )
}
