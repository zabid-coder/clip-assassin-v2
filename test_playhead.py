import sys
sys.path.append("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

fps = project.GetSetting("timelineFrameRate")
start_tc = timeline.GetSetting("timelineStartTimecode")
start_frame = timeline.GetStartFrame()
curr_tc = timeline.GetCurrentTimecode()

print(f"FPS: {fps}")
print(f"Start TC: {start_tc}")
print(f"Start Frame: {start_frame}")
print(f"Current TC: {curr_tc}")
