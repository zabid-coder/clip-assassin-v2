import { Library, UploadCloud, Box } from 'lucide-react'
import { ActionButton } from '../components/ui'

interface Props {
  templates: string[]
  fetchTemplates: () => void
  loading: Record<string, boolean>
  setLoading: React.Dispatch<React.SetStateAction<Record<string, boolean>>>
  runTask: (endpoint: string, payload: any, buttonId: string) => void
  addLog: (msg: string, type: 'info' | 'success' | 'error') => void
}

export function TemplatesPage({ templates, fetchTemplates, loading, setLoading, runTask, addLog }: Props) {
  return (
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
        onDragOver={(e) => { e.preventDefault(); setLoading(prev => ({ ...prev, drop: true })) }}
        onDragLeave={(e) => { e.preventDefault(); setLoading(prev => ({ ...prev, drop: false })) }}
        onDrop={(e) => {
          e.preventDefault()
          setLoading(prev => ({ ...prev, drop: false }))
          if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            addLog("Browser security prevents reading the absolute path. Please place the file in the 'templates' folder directly.", 'error')
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
  )
}
