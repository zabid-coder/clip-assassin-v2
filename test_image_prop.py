import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
project = resolve.GetProjectManager().GetCurrentProject()
media_pool = project.GetMediaPool()

image_item = None
for item in media_pool.GetRootFolder().GetClipList():
    if item.GetClipProperty("Type") == "Still":
        image_item = item
        break

if image_item:
    print("Duration:", image_item.GetClipProperty("Duration"))
    print("Frames:", image_item.GetClipProperty("Frames"))
else:
    print("No still image found")
