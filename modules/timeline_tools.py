from time_parser import parse_timecodes


def _seconds_to_frames(seconds, fps):
    return int(round(seconds * fps))


def cut_video(core, timecodes_text, reverse_mode=False, target_clip_name=""):
    """
    Cut clips within (or outside, in reverse mode) the specified timecode ranges.

    Args:
        core: ResolveConnection instance
        timecodes_text: Multi-line string of "start-end" ranges
        reverse_mode: If True, keep only clips inside the ranges (delete outside)
        target_clip_name: Optional substring filter to limit cuts to matching clips
    """
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline:
            return False, "No active timeline found."

        fps_str = timeline.GetSetting("timelineFrameRate") or "30"
        fps = float(fps_str)

        parsed_ranges, parse_errors = parse_timecodes(timecodes_text, fps)
        if not parsed_ranges:
            msg = "Could not parse any valid timecodes."
            if parse_errors:
                msg += " Errors: " + "; ".join(parse_errors)
            return False, msg

        items = timeline.GetItemListInTrack("video", 1)
        if not items:
            return False, "No clips found on Video Track 1."

        if target_clip_name:
            items = [i for i in items if target_clip_name.lower() in i.GetName().lower()]
            if not items:
                return False, f"No clip found matching '{target_clip_name}'"

        # Convert range seconds to timeline-relative frames using the timeline's start offset
        timeline_start = int(timeline.GetStartFrame())
        frame_ranges = [
            (
                timeline_start + _seconds_to_frames(r_start, fps),
                timeline_start + _seconds_to_frames(r_end, fps),
            )
            for (r_start, r_end) in parsed_ranges
        ]

        clips_to_delete = []

        for item in items:
            clip_start = item.GetStart()
            clip_end = item.GetEnd()

            inside_any_range = False
            for (r_start, r_end) in frame_ranges:
                # A clip is "inside a range" when it fully sits within [r_start, r_end)
                if clip_start >= r_start and clip_end <= r_end:
                    inside_any_range = True
                    break

            if reverse_mode:
                # Reverse: keep clips INSIDE ranges, delete everything else
                if not inside_any_range:
                    clips_to_delete.append(item)
            else:
                # Normal: delete clips inside ranges
                if inside_any_range:
                    clips_to_delete.append(item)

        if not clips_to_delete:
            hint = "outside" if reverse_mode else "inside"
            return False, f"No clips found {hint} the specified ranges to cut."

        timeline.DeleteClips(clips_to_delete, True)
        mode_str = "outside" if reverse_mode else "inside"
        return True, f"Cut {mode_str}: Deleted {len(clips_to_delete)} clips and rippled gaps."

    except Exception as e:
        return False, f"Error: {str(e)}"

def pick_clips_from_timeline(core, names_text):
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No active timeline found."
        
        items = timeline.GetItemListInTrack("video", 1)
        if not items: return False, "No clips found on Video Track 1."
        
        search_terms = [t.strip().lower() for t in names_text.split(",") if t.strip()]
        matched_clips = []
        
        for item in items:
            name = item.GetName().lower()
            for term in search_terms:
                if '-' in term:
                    try:
                        start_str, end_str = term.split('-')
                        start_num = int(start_str)
                        end_num = int(end_str)

                        import re
                        nums = re.findall(r'\d+', name)
                        if nums:
                            clip_num = int(nums[-1])
                            if start_num <= clip_num <= end_num:
                                matched_clips.append(item)
                                break
                    except (ValueError, IndexError):
                        pass
                else:
                    if term in name:
                        matched_clips.append(item)
                        break
                        
        if not matched_clips:
            return False, "No matching clips found."
            
        media_pool_items = []
        for c in matched_clips:
            mpi = c.GetMediaPoolItem()
            if mpi: media_pool_items.append(mpi)
            
        if not media_pool_items:
            return False, "Could not resolve Media Pool items for matches."
            
        new_timeline = core.media_pool.CreateEmptyTimeline(f"Picked Clips - {len(media_pool_items)}")
        if not new_timeline:
            return False, "Failed to create new timeline."
            
        core.project.SetCurrentTimeline(new_timeline)
        core.media_pool.AppendToTimeline(media_pool_items)
        
        return True, f"✓ Successfully extracted {len(media_pool_items)} clips into a new timeline."
    except Exception as e:
        return False, f"Error: {str(e)}"

def merge_timelines(core, names_text):
    try:
        if not names_text.strip(): return False, "No timeline names provided."
        
        names = [n.strip().lower() for n in names_text.split(',')]
        timelines_to_merge = []
        
        count = core.project.GetTimelineCount()
        for i in range(1, count + 1):
            t = core.project.GetTimelineByIndex(i)
            if t.GetName().lower() in names:
                timelines_to_merge.append(t)
                
        if not timelines_to_merge:
            return False, "None of the specified timelines were found."
            
        master = core.media_pool.CreateEmptyTimeline("Master Merged Timeline")
        core.project.SetCurrentTimeline(master)
        
        for t in timelines_to_merge:
            mpi = t.GetMediaPoolItem()
            if mpi:
                core.media_pool.AppendToTimeline([{
                    "mediaPoolItem": mpi,
                    "startFrame": 0,
                    "endFrame": t.GetEndFrame()
                }])
                
        return True, f"✓ Merged {len(timelines_to_merge)} timelines into 'Master Merged Timeline'."
    except Exception as e:
        return False, f"Error: {str(e)}"

def markers_to_timeline(core, target_color):
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No timeline open."
        
        markers = timeline.GetMarkers()
        if not markers: return False, "No markers found."
        
        items = timeline.GetItemListInTrack("video", 1)
        if not items: return False, "No video clips found."
        
        marked_clips = []
        for item in items:
            start = item.GetStart()
            end = item.GetEnd()
            
            for frame_id, marker_data in markers.items():
                if target_color == "All" or marker_data['color'] == target_color:
                    if start <= int(frame_id) <= end:
                        marked_clips.append(item)
                        break
                        
        if not marked_clips:
            return False, f"No clips found with {target_color} markers."
            
        mp_items = [c.GetMediaPoolItem() for c in marked_clips if c.GetMediaPoolItem()]
        if not mp_items: return False, "Could not resolve Media Pool items."
        
        new_timeline = core.media_pool.CreateEmptyTimeline(f"Extracted {target_color} Markers")
        core.project.SetCurrentTimeline(new_timeline)
        core.media_pool.AppendToTimeline(mp_items)
        
        return True, f"✓ Extracted {len(mp_items)} marked clips to a new timeline."
    except Exception as e:
        return False, f"Error: {str(e)}"

def filter_by_flag(core, target_color):
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No timeline open."
        
        items = timeline.GetItemListInTrack("video", 1)
        if not items: return False, "No video clips found."
        
        flagged_clips = []
        for item in items:
            flags = item.GetFlagList()
            if target_color in flags:
                flagged_clips.append(item)
                
        if not flagged_clips:
            return False, f"No clips found with {target_color} flags."
            
        mp_items = [c.GetMediaPoolItem() for c in flagged_clips if c.GetMediaPoolItem()]
        
        new_timeline = core.media_pool.CreateEmptyTimeline(f"Extracted {target_color} Flags")
        core.project.SetCurrentTimeline(new_timeline)
        core.media_pool.AppendToTimeline(mp_items)
        
        return True, f"✓ Extracted {len(mp_items)} flagged clips to a new timeline."
    except Exception as e:
        return False, f"Error: {str(e)}"

def apply_watermark_track(core, image_path):
    import os
    try:
        if not os.path.exists(image_path):
            return False, "Image file not found."
            
        timeline = core.project.GetCurrentTimeline()
        if not timeline: return False, "No timeline open."
        
        media_storage = core.resolve.GetMediaStorage()
        items = media_storage.AddItemListToMediaPool(image_path)
        if not items: return False, "Could not import image."
        
        timeline.AddTrack("video")
        top_track = timeline.GetTrackCount("video")
        
        start_frame = timeline.GetStartFrame()
        end_frame = timeline.GetEndFrame()
        current_record = start_frame
        
        all_appended_items = []
        
        while current_record < end_frame:
            remaining = end_frame - current_record
            appended = core.media_pool.AppendToTimeline([{
                "mediaPoolItem": items[0],
                "startFrame": 0,
                "endFrame": remaining,
                "trackIndex": top_track,
                "recordFrame": current_record
            }])
            
            if not appended or len(appended) == 0:
                break
                
            all_appended_items.extend(appended)
            
            clip_duration = appended[0].GetDuration()
            if clip_duration <= 0:
                break
                
            current_record += clip_duration
            
        if all_appended_items:
            compound_clip = timeline.CreateCompoundClip(all_appended_items, {"name": "Watermark Overlay"})
            
            # Apply dynamic transform based on timeline resolution
            try:
                w = float(timeline.GetSetting("timelineResolutionWidth") or 1920.0)
                h = float(timeline.GetSetting("timelineResolutionHeight") or 1080.0)
                
                zoom = 0.170
                # Scale Pan and Tilt proportionally from the 1920x1080 baseline
                pan = 725.0 * (w / 1920.0)
                tilt = 544.0 * (h / 1080.0)
                
                if compound_clip:
                    compound_clip.SetProperty("ZoomX", zoom)
                    compound_clip.SetProperty("ZoomY", zoom)
                    compound_clip.SetProperty("Pan", pan)
                    compound_clip.SetProperty("Tilt", tilt)
            except Exception:
                pass
            
        return True, f"✓ Watermark added and compounded on Track {top_track}."
    except Exception as e:
        return False, f"Error: {str(e)}"
