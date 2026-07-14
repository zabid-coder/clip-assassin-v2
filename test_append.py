import sys
import os
sys.path.append("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import DaVinciResolveScript as dvr
import time_parser

resolve = dvr.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

fps = float(project.GetSetting("timelineFrameRate"))
tc = timeline.GetCurrentTimecode()
secs = time_parser.parse_time(tc, fps)
record_frame = int(round(secs * fps))

print(f"TC: {tc} -> Secs: {secs} -> Frame: {record_frame}")
