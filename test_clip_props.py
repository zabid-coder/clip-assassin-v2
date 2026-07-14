import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

# Get the first clip in the first video track
items = timeline.GetItemListInTrack("video", 1)
if items:
    print(items[0].GetProperty())
else:
    print("No items on video track 1")
