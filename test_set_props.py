import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

items = timeline.GetItemListInTrack("video", 1)
if items:
    clip = items[0]
    res = clip.SetProperty("Pan", 725.0)
    print("Set Pan 725:", res)
    res = clip.SetProperty("Tilt", 544.0)
    print("Set Tilt 544:", res)
    res = clip.SetProperty("ZoomX", 0.170)
    print("Set ZoomX:", res)
    res = clip.SetProperty("ZoomY", 0.170)
    print("Set ZoomY:", res)
else:
    print("No items")
