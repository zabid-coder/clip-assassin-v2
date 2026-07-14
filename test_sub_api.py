import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
project = resolve.GetProjectManager().GetCurrentProject()
res1 = project.SetRenderSettings({"ExportSubtitles": True})
res2 = project.SetRenderSettings({"ExportSubtitle": True})
res3 = project.SetRenderSettings({"SubtitleExportType": "BurnIn"})
print("ExportSubtitles:", res1)
print("ExportSubtitle:", res2)
print("SubtitleExportType:", res3)
