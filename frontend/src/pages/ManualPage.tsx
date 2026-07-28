import { BookOpen, Activity, FolderPlus, Sparkles, Scissors, Combine, MonitorUp, Library } from 'lucide-react'

export function ManualPage() {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
      <div className="mb-2">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <BookOpen className="text-brand-primary" /> User Manual
        </h2>
        <p className="text-xs text-white/50 mt-1">Step-by-step documentation for all Clip Assassin tools.</p>
      </div>

      <div className="space-y-4">
        <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
          <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Activity size={16} /> Dashboard & Basics</h3>
          <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
            <li><strong>Global Selection:</strong> Use the top-left dropdown to instantly switch your active timeline in Resolve.</li>
            <li><strong>Keyboard Shortcuts:</strong> Press <code>Cmd+1</code> to <code>6</code> to switch tabs. Press <code>Cmd+R</code> to reconnect.</li>
            <li><strong>Smart Presets:</strong> The app automatically saves your render paths and dropdown selections locally.</li>
            <li><strong>Undo:</strong> If you make a mistake, simply press <code>Ctrl+Z</code> inside DaVinci Resolve to undo any automated action.</li>
            <li><strong>Pin to Dashboard:</strong> Click the Pin icon on any tool card across the app to pin it to your Dashboard for quick access.</li>
          </ul>

          <div className="mt-4 p-4 bg-brand-primary/10 border border-brand-primary/30 rounded-xl text-xs text-white/80 space-y-1.5 leading-relaxed">
            <p className="font-bold text-brand-primary flex items-center gap-1.5">⚡ First-Time Setup: Enabling DaVinci Resolve API Access</p>
            <p>If you see <code className="text-rose-400">Could not connect to DaVinci Resolve</code>, follow these 4 quick steps inside Resolve:</p>
            <p>1. Open <strong>DaVinci Resolve</strong>.</p>
            <p>2. Press <strong>Cmd + ,</strong> (or Ctrl + ,) to open <strong>Preferences</strong>.</p>
            <p>3. Go to <strong>System</strong> &gt; <strong>General</strong>.</p>
            <p>4. Change <strong>External scripting using</strong> to <strong>Local</strong>.</p>
            <p className="text-white/60 italic mt-1">• Click Save, close any open modal dialogs (like Preferences), and restart DaVinci Resolve.</p>
          </div>
        </div>

        <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
          <h3 className="text-brand-primary font-semibold mb-3 flex items-center gap-2"><FolderPlus size={16} /> Master Ingest & Folder Template Reference</h3>
          <div className="text-sm text-white/70 space-y-3">
            <p><strong>1. Master Folder Setup:</strong> Creates date-prefixed folders (<code>YYYY-MM-DD_[Client]_[Project]</code>) on disk with standard sub-folder templates.</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs bg-black/40 p-4 rounded-xl border border-white/5 leading-relaxed font-mono">
              <div>
                <span className="text-brand-primary font-bold block mb-1">Standard Video & Film</span>
                • Raw Footages/Card 01<br />
                • Raw Footages/Card 02<br />
                • Davinci Resolve Database<br />
                • Logos & Branding<br />
                • BG Music<br />
                • After Effects / Photoshop<br />
                • Exports & Documents
              </div>
              <div>
                <span className="text-cyan-400 font-bold block mb-1">Social Media & Reels</span>
                • Raw Footages/Card 01<br />
                • Davinci Resolve Database<br />
                • Logos & Branding<br />
                • Audio & Music<br />
                • Graphics & Assets<br />
                • Exports
              </div>
              <div>
                <span className="text-emerald-400 font-bold block mb-1">Commercial / Corporate</span>
                • Raw Footages/Camera A & B<br />
                • Davinci Resolve Database<br />
                • Logos & Branding<br />
                • Audio & Voiceover<br />
                • Motion Graphics<br />
                • Client Approvals & Exports
              </div>
            </div>
            <p><strong>2. Auto Ingest Workflow:</strong> Connects to your active DaVinci Resolve session, creates a versioned project named after your Master Folder, configures working folder locations, imports camera footage into Media Pool Bins, and builds individual Card Timelines inside the <code className="text-brand-primary">Projects</code> bin.</p>
          </div>
        </div>

        <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
          <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Sparkles size={16} /> Magic Tools</h3>
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
          <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Scissors size={16} /> Cut & Trim Tools</h3>
          <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
            <li><strong>Timecode Cutter:</strong> Slices your timeline at the timecodes, timestamps, or frame numbers you enter.</li>
            <li><strong>Clip Picker:</strong> Builds a new timeline from the specific clip numbers you list.</li>
            <li><strong>Markers to Timeline:</strong> Extracts every clip marked with the selected color into a fresh timeline.</li>
            <li><strong>Flag Filter:</strong> Pulls only the clips flagged with the color you choose.</li>
          </ul>
        </div>

        <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
          <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Combine size={16} /> Process Tools</h3>
          <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
            <li><strong>Merge Timelines:</strong> Appends the timelines you select into one master timeline, in order.</li>
            <li><strong>Watermark Track:</strong> Places your logo across the top track of the whole video.</li>
            <li><strong>Auto J-Cut / L-Cut:</strong> Offsets audio at each cut point to smooth interview edits.</li>
            <li><strong>Silence Remover:</strong> Detects dead air on Track 1 and ripple-deletes it automatically.</li>
          </ul>
        </div>

        <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
          <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><MonitorUp size={16} /> Export Tools</h3>
          <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
            <li><strong>Batch Timeline Render:</strong> Batch renders multiple selected timelines using a custom DaVinci Resolve preset.</li>
            <li><strong>Extract Thumbnails:</strong> Saves a still frame at every marker (or selection) to your chosen folder.</li>
            <li><strong>Auto YouTube Chapters:</strong> Generates timestamped chapters from your timeline markers.</li>
            <li><strong>Client Shotlist / Document Exporter:</strong> Exports your clip list as a CSV for client review.</li>
          </ul>
        </div>

        <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
          <h3 className="text-brand-primary font-semibold mb-2 flex items-center gap-2"><Library size={16} /> Templates</h3>
          <ul className="text-sm text-white/70 space-y-2 list-disc pl-5">
            <li><strong>Asset Library:</strong> Imports .drfx templates from your plugin folder straight into the Media Pool.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
