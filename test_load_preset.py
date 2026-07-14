import sys
import json
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
project = resolve.GetProjectManager().GetCurrentProject()
res = project.LoadRenderPreset("/Users/audiovisual/Desktop/Clip_Assassin_Resolve-v2.0.0/test_preset.xml")
print("Load preset result:", res)
