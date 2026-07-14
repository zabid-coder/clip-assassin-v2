import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
project = resolve.GetProjectManager().GetCurrentProject()
res = project.SetRenderSettings({
    "Format": "mp4",
    "VideoCodec": "H264",
    "ExportVideo": True,
    "SubtitleExportType": 0, # wait, let's try some subtitle keys
})
print("Result with VideoCodec:", res)
res2 = project.SetRenderSettings({
    "Format": "mp4",
    "Codec": "H264"
})
print("Result with Codec:", res2)
