"""
BadWords Integration — Marker Scanner & Timeline Cleaner
Scans color-coded markers from BadWords-generated timelines
and creates clean timelines by removing marked segments.
"""


def scan_markers(core):
    """
    Scan the current timeline for all markers and return a summary
    grouped by color with counts and total duration.
    
    Returns:
        dict with keys: success, markers (list), summary (dict of color -> count),
        total_marked_seconds, timeline_name
    """
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline:
            return {"success": False, "message": "No active timeline found."}

        fps = float(timeline.GetSetting("timelineFrameRate") or 30)
        timeline_name = timeline.GetName()
        markers = timeline.GetMarkers()

        if not markers:
            return {
                "success": False,
                "message": f"No markers found on timeline '{timeline_name}'. "
                           "Make sure you have run BadWords analysis first."
            }

        # Build marker list and color summary
        marker_list = []
        color_summary = {}
        total_marked_frames = 0

        for frame_id, marker_data in markers.items():
            color = marker_data.get("color", "Unknown")
            duration = int(marker_data.get("duration", 1))
            name = marker_data.get("name", "")
            note = marker_data.get("note", "")

            marker_list.append({
                "frame": int(frame_id),
                "color": color,
                "duration": duration,
                "name": name,
                "note": note,
                "time_seconds": round(int(frame_id) / fps, 2)
            })

            if color not in color_summary:
                color_summary[color] = {"count": 0, "total_frames": 0}
            color_summary[color]["count"] += 1
            color_summary[color]["total_frames"] += duration
            total_marked_frames += duration

        # Convert frames to seconds in summary
        for color in color_summary:
            color_summary[color]["total_seconds"] = round(
                color_summary[color]["total_frames"] / fps, 1
            )

        return {
            "success": True,
            "timeline_name": timeline_name,
            "fps": fps,
            "total_markers": len(marker_list),
            "total_marked_seconds": round(total_marked_frames / fps, 1),
            "summary": color_summary,
            "markers": marker_list
        }

    except Exception as e:
        return {"success": False, "message": f"Error scanning markers: {str(e)}"}


def clean_timeline(core, colors_to_remove):
    """
    Create a new timeline that excludes segments covered by markers 
    of the specified colors.
    
    Args:
        core: ResolveConnection instance
        colors_to_remove: list of color strings to remove (e.g. ["Red", "Blue"])
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline:
            return False, "No active timeline found."

        if not colors_to_remove:
            return False, "No colors selected for removal."

        fps = float(timeline.GetSetting("timelineFrameRate") or 30)
        timeline_name = timeline.GetName()
        markers = timeline.GetMarkers()

        if not markers:
            return False, "No markers found on the current timeline."

        # Collect frame ranges to remove
        remove_ranges = []
        removed_count = 0

        for frame_id, marker_data in markers.items():
            color = marker_data.get("color", "")
            if color in colors_to_remove:
                start_frame = int(frame_id)
                duration = int(marker_data.get("duration", 1))
                end_frame = start_frame + duration
                remove_ranges.append((start_frame, end_frame))
                removed_count += 1

        if not remove_ranges:
            return False, f"No markers found matching colors: {', '.join(colors_to_remove)}"

        # Sort ranges by start frame
        remove_ranges.sort(key=lambda r: r[0])

        # Merge overlapping ranges
        merged = [remove_ranges[0]]
        for start, end in remove_ranges[1:]:
            if start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))

        # Calculate inverse ranges (segments to KEEP)
        timeline_start = int(timeline.GetStartFrame())
        timeline_end = int(timeline.GetEndFrame())

        keep_ranges = []
        cursor = timeline_start

        for rm_start, rm_end in merged:
            if cursor < rm_start:
                keep_ranges.append((cursor, rm_start))
            cursor = max(cursor, rm_end)

        if cursor < timeline_end:
            keep_ranges.append((cursor, timeline_end))

        if not keep_ranges:
            return False, "Nothing left after removing all marked segments. The entire timeline is marked."

        # Get the timeline as a media pool item for re-assembly
        timeline_mpi = core.get_clip_by_name(timeline_name)
        if not timeline_mpi:
            # Fallback: try to find it by iterating
            count = core.project.GetTimelineCount()
            for i in range(1, count + 1):
                t = core.project.GetTimelineByIndex(i)
                if t and t.GetName() == timeline_name:
                    # Use the timeline's media pool item
                    root = core.media_pool.GetRootFolder()
                    clips = root.GetClipList()
                    for c in clips:
                        if c.GetName() == timeline_name:
                            timeline_mpi = c
                            break
                    break

        if not timeline_mpi:
            return False, (
                "Could not find the timeline in Media Pool. "
                "This can happen if the timeline was recently created. "
                "Try switching to another timeline and back, then retry."
            )

        # Create new clean timeline
        new_name = f"Cleaned - {timeline_name}"

        # Handle duplicate names
        existing_count = 1
        original_name = new_name
        while core._timeline_exists(new_name):
            existing_count += 1
            new_name = f"{original_name} ({existing_count})"

        new_timeline = core.media_pool.CreateEmptyTimeline(new_name)
        if not new_timeline:
            return False, "Failed to create new timeline."

        core.project.SetCurrentTimeline(new_timeline)

        # Append each clean segment
        segments_added = 0
        for keep_start, keep_end in keep_ranges:
            clip_info = {
                "mediaPoolItem": timeline_mpi,
                "startFrame": keep_start,
                "endFrame": keep_end,
            }
            result = core.media_pool.AppendToTimeline([clip_info])
            if result:
                segments_added += 1

        # Calculate stats
        total_removed_frames = sum(e - s for s, e in merged)
        total_kept_frames = sum(e - s for s, e in keep_ranges)
        removed_seconds = round(total_removed_frames / fps, 1)
        kept_seconds = round(total_kept_frames / fps, 1)

        colors_str = ", ".join(colors_to_remove)
        summary = (
            f"✓ BadWords Cleaner — Mission accomplished!\n\n"
            f"Source: {timeline_name}\n"
            f"New Timeline: {new_name}\n"
            f"Markers removed: {removed_count} ({colors_str})\n"
            f"Time removed: {removed_seconds}s\n"
            f"Clean duration: {kept_seconds}s\n"
            f"Segments: {segments_added}"
        )

        return True, summary

    except Exception as e:
        return False, f"Error cleaning timeline: {str(e)}"
