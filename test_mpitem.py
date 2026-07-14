import sys
sys.path.append("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

item = timeline.InsertGeneratorIntoTimeline("Adjustment Clip")
if item:
    mp_item = item.GetMediaPoolItem()
    print(f"MediaPoolItem: {mp_item}")
    
    # Try to delete the inserted item, wait, the API doesn't have an explicit delete timeline item, 
    # but we can try to find a way or just leave it and let the user know, 
    # OR maybe we can just use mp_item directly!
    
    start_frame = int(timeline.GetStartFrame())
    end_frame = int(timeline.GetEndFrame())
    duration = end_frame - start_frame
    if duration > 0:
        append_info = [{
            "mediaPoolItem": mp_item,
            "startFrame": 0, 
            "endFrame": duration - 1,
            "trackIndex": 3
        }]
        res = resolve.GetProjectManager().GetCurrentProject().GetMediaPool().AppendToTimeline(append_info)
        print(f"Append result: {res}")
