import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

# Get the compound clip on track 6
# Assuming the user already has the watermark overlay there
items = timeline.GetItemListInTrack("video", timeline.GetTrackCount("video"))
if items:
    for item in items:
        if item.GetName() == "Watermark Overlay":
            res = item.SetProperty("ZoomX", 0.5)
            print("Set ZoomX on compound clip:", res)
            break
else:
    print("No items on top track")
