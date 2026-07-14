import sys
sys.path.append("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

item = timeline.InsertGeneratorIntoTimeline("Adjustment Clip")
print(f"RightOffset: {item.GetRightOffset(False)}")
