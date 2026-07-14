import sys
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if RESOLVE_SCRIPT_API not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API)
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()
media_pool = project.GetMediaPool()

# Just find an image in media pool to test
image_item = None
for item in media_pool.GetRootFolder().GetClipList():
    if item.GetClipProperty("Type") == "Still":
        image_item = item
        break

if not image_item:
    print("No still image found in root folder")
    sys.exit()

timeline.AddTrack("video")
top_track = timeline.GetTrackCount("video")

start_frame = timeline.GetStartFrame()
end_frame = timeline.GetEndFrame()
duration = end_frame - start_frame

print(f"Top track: {top_track}, Duration: {duration}")

result = media_pool.AppendToTimeline([{
    "mediaPoolItem": image_item,
    "startFrame": 0,
    "endFrame": duration,
    "trackIndex": top_track,
    "recordFrame": start_frame
}])

print("Appended:", result)
if result:
    print("Duration of inserted item:", result[0].GetDuration())

