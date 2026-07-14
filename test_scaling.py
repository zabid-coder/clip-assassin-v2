import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
project = resolve.GetProjectManager().GetCurrentProject()
timeline = project.GetCurrentTimeline()

items = timeline.GetItemListInTrack("video", 1)
if items:
    clip = items[0]
    for i in range(5):
        res = clip.SetProperty("Scaling", i)
        print(f"Set Scaling to {i}: {res}")
else:
    print("No items")
