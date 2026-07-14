"""
Audio & Edit Tools — J-Cut/L-Cut generator, Audio normalization,
Render Queue Monitor, Silence detection placeholder.
"""
import os


def apply_jl_cuts(core, cut_type="j", overlap_frames=10):
    """
    Apply J-Cut or L-Cut transitions to all edit points on Video Track 1.
    
    J-Cut: Audio from next clip starts before the video transition
    L-Cut: Audio from current clip continues after the video transition
    
    Args:
        core: ResolveConnection instance
        cut_type: "j" or "l"
        overlap_frames: number of frames to offset audio
    
    Returns:
        tuple: (success, message)
    """
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline:
            return False, "No active timeline found."

        video_items = timeline.GetItemListInTrack("video", 1)
        audio_items = timeline.GetItemListInTrack("audio", 1)

        if not video_items or len(video_items) < 2:
            return False, "Need at least 2 clips on Video Track 1 for J/L cuts."

        if not audio_items:
            return False, "No audio clips found on Audio Track 1."

        cuts_applied = 0

        for i in range(len(video_items) - 1):
            try:
                current_video = video_items[i]
                next_video = video_items[i + 1]

                if i < len(audio_items) - 1:
                    current_audio = audio_items[i]
                    next_audio = audio_items[i + 1]

                    if cut_type == "j":
                        # J-Cut: extend next audio backward (start earlier)
                        next_audio_start = next_audio.GetStart()
                        new_start = max(0, next_audio_start - overlap_frames)
                        next_audio.SetProperty("Start", new_start)
                        cuts_applied += 1
                    else:
                        # L-Cut: extend current audio forward (end later)
                        current_audio_end = current_audio.GetEnd()
                        new_end = current_audio_end + overlap_frames
                        current_audio.SetProperty("End", new_end)
                        cuts_applied += 1
            except Exception:
                continue

        if cuts_applied == 0:
            return False, (
                f"Could not apply {cut_type.upper()}-Cuts. "
                "DaVinci Resolve's API has limited support for direct audio trimming. "
                "Try using the Trim tool manually in the Edit page."
            )

        cut_name = "J-Cut" if cut_type == "j" else "L-Cut"
        return True, f"✓ Applied {cuts_applied} {cut_name} transitions with {overlap_frames} frame overlap."

    except Exception as e:
        return False, f"Error applying cuts: {str(e)}"


def get_render_status(core):
    """
    Get the current render queue status.
    
    Returns:
        dict with render job information
    """
    try:
        if not core.project:
            return {"success": False, "message": "No project connected"}

        render_jobs = core.project.GetRenderJobList()
        if not render_jobs:
            return {
                "success": True,
                "jobs": [],
                "total": 0,
                "message": "Render queue is empty."
            }

        job_list = []
        for job in render_jobs:
            job_info = {
                "id": job.get("JobId", ""),
                "name": job.get("TimelineName", "Unknown"),
                "status": job.get("RenderStatus", "Unknown"),
                "progress": job.get("CompletionPercentage", 0),
                "output_dir": job.get("TargetDir", ""),
                "format": job.get("FormatWidth", "?") + "x" + job.get("FormatHeight", "?"),
            }

            # Check if currently rendering
            if job.get("RenderStatus") == "Rendering":
                status_info = core.project.GetRenderJobStatus(job["JobId"])
                if status_info:
                    job_info["progress"] = status_info.get("CompletionPercentage", 0)
                    job_info["time_remaining"] = status_info.get("EstimatedTimeRemainingInMs", 0)

            job_list.append(job_info)

        # Count statuses
        completed = sum(1 for j in job_list if j["status"] == "Complete")
        rendering = sum(1 for j in job_list if j["status"] == "Rendering")
        queued = sum(1 for j in job_list if j["status"] == "Ready")
        failed = sum(1 for j in job_list if j["status"] == "Failed")

        return {
            "success": True,
            "jobs": job_list,
            "total": len(job_list),
            "completed": completed,
            "rendering": rendering,
            "queued": queued,
            "failed": failed
        }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


def detect_silence(core, threshold_db=-40, min_silence_ms=500, padding_ms=100):
    """
    Detect silent sections in the current timeline's audio and create 
    a new timeline without them.
    
    Note: DaVinci Resolve API does not expose raw audio waveforms directly.
    This function works by analyzing the audio via rendered export + pydub,
    or by using timeline markers as a fallback.
    
    Args:
        core: ResolveConnection instance
        threshold_db: Silence threshold in dB (default: -40)
        min_silence_ms: Minimum silence duration in ms to detect
        padding_ms: Audio padding around cuts in ms
    
    Returns:
        tuple: (success, message)
    """
    try:
        timeline = core.project.GetCurrentTimeline()
        if not timeline:
            return False, "No active timeline found."

        timeline_name = timeline.GetName()
        fps = float(timeline.GetSetting("timelineFrameRate") or 30)
        start_frame = int(timeline.GetStartFrame())
        end_frame = int(timeline.GetEndFrame())
        total_frames = end_frame - start_frame

        if total_frames <= 0:
            return False, "Timeline appears to be empty."

        # Try to use pydub for audio analysis
        try:
            from pydub import AudioSegment
            from pydub.silence import detect_nonsilent
        except ImportError:
            return False, (
                "Silence detection requires the 'pydub' library.\n"
                "Install it with: pip install pydub\n"
                "You also need ffmpeg installed on your system."
            )

        # Export audio to a temp WAV for analysis
        import tempfile
        temp_dir = tempfile.mkdtemp()
        temp_audio = os.path.join(temp_dir, "temp_audio.wav")

        # Use Resolve's render to export audio only
        core.project.SetCurrentTimeline(timeline)
        
        render_settings = {
            "SelectAllFrames": True,
            "TargetDir": temp_dir,
            "CustomName": "temp_audio",
            "FormatWidth": 1920,
            "FormatHeight": 1080,
            "AudioCodec": "LinearPCM",
        }

        core.project.SetRenderSettings(render_settings)
        pid = core.project.AddRenderJob()
        
        if not pid:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False, (
                "Could not create audio render job. "
                "As a workaround, manually export the audio as WAV, "
                "then use the silence detection on the exported file."
            )

        core.project.StartRendering(pid)
        
        # Wait for render (max 120s)
        import time
        for _ in range(240):
            status = core.project.GetRenderJobStatus(pid)
            if status and status.get("RenderStatus") == "Complete":
                break
            time.sleep(0.5)

        # Find the rendered audio file
        audio_file = None
        for f in os.listdir(temp_dir):
            if f.endswith(('.wav', '.mp3', '.aac', '.flac')):
                audio_file = os.path.join(temp_dir, f)
                break

        if not audio_file or not os.path.exists(audio_file):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False, "Audio export failed. Could not find rendered audio file."

        # Analyze silence
        audio = AudioSegment.from_file(audio_file)
        non_silent_ranges = detect_nonsilent(
            audio, 
            min_silence_len=min_silence_ms, 
            silence_thresh=threshold_db
        )

        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

        if not non_silent_ranges:
            return False, "No speech detected. The entire timeline appears to be silent."

        # Add padding
        padded_ranges = []
        for start_ms, end_ms in non_silent_ranges:
            padded_start = max(0, start_ms - padding_ms)
            padded_end = min(len(audio), end_ms + padding_ms)
            padded_ranges.append((padded_start, padded_end))

        # Merge overlapping ranges
        merged = [padded_ranges[0]]
        for start, end in padded_ranges[1:]:
            if start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))

        # Convert ms to frames
        frame_ranges = []
        for start_ms, end_ms in merged:
            start_f = start_frame + int((start_ms / 1000.0) * fps)
            end_f = start_frame + int((end_ms / 1000.0) * fps)
            frame_ranges.append((start_f, end_f))

        # Create new timeline with only non-silent parts
        timeline_mpi = core.get_clip_by_name(timeline_name)
        if not timeline_mpi:
            return False, "Could not find timeline in Media Pool."

        new_name = f"No Silence - {timeline_name}"
        count = 1
        original = new_name
        while core._timeline_exists(new_name):
            count += 1
            new_name = f"{original} ({count})"

        new_timeline = core.media_pool.CreateEmptyTimeline(new_name)
        if not new_timeline:
            return False, "Failed to create new timeline."

        core.project.SetCurrentTimeline(new_timeline)

        segments_added = 0
        for keep_start, keep_end in frame_ranges:
            result = core.media_pool.AppendToTimeline([{
                "mediaPoolItem": timeline_mpi,
                "startFrame": keep_start,
                "endFrame": keep_end,
            }])
            if result:
                segments_added += 1

        # Stats
        original_duration = len(audio) / 1000.0
        kept_duration = sum((e - s) / 1000.0 for s, e in merged)
        removed_duration = original_duration - kept_duration

        return True, (
            f"✓ Silence Remover — Done!\n\n"
            f"Source: {timeline_name}\n"
            f"New Timeline: {new_name}\n"
            f"Original: {original_duration:.1f}s\n"
            f"Removed: {removed_duration:.1f}s of silence\n"
            f"Clean: {kept_duration:.1f}s ({segments_added} segments)\n"
            f"Settings: threshold={threshold_db}dB, min_silence={min_silence_ms}ms, padding={padding_ms}ms"
        )

    except Exception as e:
        return False, f"Error during silence detection: {str(e)}"
