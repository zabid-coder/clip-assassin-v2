def batch_render(core, timelines, preset_name, target_dir):
    try:
        if not target_dir or str(target_dir).strip() == "":
            return False, "Error: Please specify a Save Directory first."
        if not timelines: return False, "No timelines selected."
        
        jobs_added = 0
        for t_name in timelines:
            # Find the timeline by name
            timeline = None
            for i in range(1, core.project.GetTimelineCount() + 1):
                t = core.project.GetTimelineByIndex(i)
                if t.GetName() == t_name:
                    timeline = t
                    break
            
            if not timeline:
                continue
                
            core.project.SetCurrentTimeline(timeline)
            
            if preset_name and str(preset_name).strip() != "":
                if not core.project.LoadRenderPreset(preset_name):
                    # Warning if preset doesn't exist but we still try to render
                    pass
            
            core.project.SetRenderSettings({
                "TargetDir": target_dir,
                "CustomName": timeline.GetName(),
            })
            job_id = core.project.AddRenderJob()
            if job_id: jobs_added += 1
                
        return True, f"✓ Added {jobs_added} jobs to Render Queue.\nOpen Deliver page to start rendering."
    except Exception as e:
        return False, f"Error: {str(e)}"

def extract_thumbnails(core, mode, target_dir):
    try:
        if not target_dir or str(target_dir).strip() == "":
            return False, "Error: Please specify a Save Directory first."
            
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No timeline open."
        
        frames_to_grab = []
        if mode == "Markers":
            markers = timeline.GetMarkers()
            for frame_id in markers:
                frames_to_grab.append(int(frame_id))
        else: # Center frame
            start = int(timeline.GetStartFrame())
            end = int(timeline.GetEndFrame())
            frames_to_grab.append((start + end) // 2)
            
        if not frames_to_grab: return False, "No frames to grab."
        
        import os
        fps = float(timeline.GetSetting("timelineFrameRate") or 30.0)
        
        for index, frame in enumerate(frames_to_grab, start=1):
            tc = frames_to_tc(frame, fps)
            timeline.SetCurrentTimecode(tc)
            
            # Resolve infers format from extension (e.g. .jpg or .png)
            file_name = f"{timeline.GetName()}_Thumbnail-{index:02d}.jpg"
            file_path = os.path.join(target_dir, file_name)
            # Replace backslashes with forward slashes for cross-platform compatibility with Resolve API
            file_path = file_path.replace("\\", "/")
            
            core.project.ExportCurrentFrameAsStill(file_path)
            
        return True, f"✓ Exported {len(frames_to_grab)} still frames to chosen directory."
    except Exception as e:
        return False, f"Error: {str(e)}"

def generate_youtube_chapters(core):
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No timeline open."
        
        markers = timeline.GetMarkers()
        if not markers: return False, "No markers found."
        
        fps = float(timeline.GetSetting("timelineFrameRate") or 30.0)
        start_frame = int(timeline.GetStartFrame())
        
        chapters = []
        for frame_id, marker in sorted(markers.items(), key=lambda x: int(x[0])):
            rel_frame = int(frame_id) - start_frame
            rel_sec = max(0, rel_frame / fps)
            
            h = int(rel_sec // 3600)
            m = int((rel_sec % 3600) // 60)
            s = int(rel_sec % 60)
            
            tc_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
            # Format: '0:00 MarkerName' with a space after timecode. If no name, just '0:00 '
            marker_name = marker['name'] if marker['name'] else ''
            chapters.append(f"{tc_str} {marker_name}")
            
        if not any(c.startswith("0:00") or c.startswith("00:00") for c in chapters):
            chapters.insert(0, "0:00 Intro")
            
        return True, "\n".join(chapters)
    except Exception as e:
        return False, f"Error: {str(e)}"

def export_csv_data(core, output_path):
    import csv
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No timeline open."
        
        items = timeline.GetItemListInTrack("video", 1)
        if not items: return False, "No video clips found."
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Clip Name", "Source Start TC", "Duration (Frames)", "Color", "Flags"])
            
            for i, item in enumerate(items, 1):
                name = item.GetName()
                duration = item.GetDuration()
                color = item.GetClipColor()
                flags = ", ".join(item.GetFlagList()) if item.GetFlagList() else ""
                
                mpi = item.GetMediaPoolItem()
                source_tc = mpi.GetClipProperty("Start TC") if mpi else ""
                
                writer.writerow([i, name, source_tc, duration, color, flags])
                
        return True, f"✓ Exported {len(items)} clips data to:\n{output_path}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def frames_to_tc(frames, fps):
    fps = round(float(fps))
    if fps == 0: fps = 30
    h = frames // (fps * 3600)
    m = (frames % (fps * 3600)) // (fps * 60)
    s = (frames % (fps * 60)) // fps
    f = frames % fps
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"

def export_shotlist_doc(core, format, output_path, template_path=""):
    import csv
    import os
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No timeline open."
        
        ext = os.path.splitext(output_path)[1]
        if not ext:
            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)
            project_name = core.project.GetName()
            safe_project_name = "".join([c for c in project_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            output_path = os.path.join(output_path, f"{safe_project_name} Shotlist.{format}").replace("\\", "/")
        
        items = timeline.GetItemListInTrack("video", 1)
        if not items: return False, "No video clips found on Track 1."
        
        fps = float(timeline.GetSetting("timelineFrameRate") or 30.0)
        
        shots = []
        for i, item in enumerate(items, 1):
            name = item.GetName()
            
            # Try to guess shot meaning
            meaning = ""
            name_lower = name.lower()
            if "wide" in name_lower or "ws" in name_lower: meaning = "Wide"
            elif "mid" in name_lower or "ms" in name_lower: meaning = "Mid"
            elif "close" in name_lower or "cu" in name_lower: meaning = "Close"
            
            start_frame = int(item.GetStart())
            end_frame = int(item.GetEnd())
            
            start_tc = frames_to_tc(start_frame, fps)
            end_tc = frames_to_tc(end_frame, fps)
            duration_frames = int(item.GetDuration())
            duration_tc = frames_to_tc(duration_frames, fps)
            
            shots.append({
                "serial": i,
                "type": meaning,
                "start_tc": start_tc,
                "end_tc": end_tc,
                "duration": duration_tc,
                "desc": name
            })
            
        if format == 'docx':
            try:
                from docxtpl import DocxTemplate
            except ImportError:
                return False, "docxtpl library is not installed. Run 'pip install docxtpl python-docx'."
                
            if not os.path.exists(template_path):
                return False, f"Template not found at: {template_path}"
                
            doc = DocxTemplate(template_path)
            context = {
                "project_name": core.project.GetName(),
                "timeline_name": timeline.GetName(),
                "shots": shots
            }
            doc.render(context)
            doc.save(output_path)
            return True, f"✓ Generated Word Shotlist to:\n{output_path}"
            
        else: # Default CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Slate/Log Number", "Timecode (Start - End)", "Duration", "Shot Type", "Description", "Primary Tag"])
                for s in shots:
                    tc_range = f"{s['start_tc']} - {s['end_tc']}"
                    writer.writerow([s["serial"], "", tc_range, s["duration"], s["type"], s["desc"], ""])
            return True, f"✓ Exported CSV Shotlist for {len(items)} clips to:\n{output_path}"
            
    except Exception as e:
        return False, f"Error exporting Shotlist: {str(e)}"
