import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
project = resolve.GetProjectManager().GetCurrentProject()
print("RecordSubtitleEnabled:", project.SetRenderSettings({"RecordSubtitleEnabled": 1}))
print("SubtitleExportFormat:", project.SetRenderSettings({"SubtitleExportFormat": 3}))
print("SubtitleRecordType:", project.SetRenderSettings({"SubtitleRecordType": 2}))
