import sys
sys.path.append("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

item = timeline.InsertGeneratorIntoTimeline("Adjustment Clip")
print(f"Original Duration: {item.GetDuration()}")
res1 = item.SetProperty("Duration", 1000)
res2 = item.SetProperty("RightOffset", 1000)
res3 = item.SetProperty("EndFrame", 1000)
print(f"SetProperty results: {res1}, {res2}, {res3}")
print(f"New Duration: {item.GetDuration()}")
