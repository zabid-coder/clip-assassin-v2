def organize_media_pool(core):
    """Organize the root media pool into Video, Audio, and Image bins"""
    if not core.media_pool:
        return False, "Not connected to Media Pool"
        
    try:
        root_folder = core.media_pool.GetRootFolder()
        items = root_folder.GetClipList()
        if not items:
            return True, "No loose clips in Root Folder to organize."
            
        folders = root_folder.GetSubFolderList()
        folder_map = {f.GetName(): f for f in folders}
        
        for cat in ["Video", "Audio", "Images"]:
            if cat not in folder_map:
                folder_map[cat] = core.media_pool.AddSubFolder(root_folder, cat)
        
        v_clips, a_clips, i_clips = [], [], []
        
        for item in items:
            ctype = item.GetClipProperty("Type")
            if "Video" in ctype:
                v_clips.append(item)
            elif "Audio" in ctype:
                a_clips.append(item)
            elif "Still" in ctype or "Image" in ctype:
                i_clips.append(item)
                
        if v_clips: core.media_pool.MoveClips(v_clips, folder_map["Video"])
        if a_clips: core.media_pool.MoveClips(a_clips, folder_map["Audio"])
        if i_clips: core.media_pool.MoveClips(i_clips, folder_map["Images"])
        
        return True, f"Organized: {len(v_clips)} Video, {len(a_clips)} Audio, {len(i_clips)} Images."
    except Exception as e:
        return False, f"Error organizing: {e}"

def create_social_timeline(core, format="9:16"):
    """Duplicate current timeline and set it to 1080x1920 (9:16) or 1080x1080 (1:1)"""
    if not core.project:
        return False, "No project connected"
        
    timeline = core.project.GetCurrentTimeline()
    if not timeline:
        return False, "No active timeline"
        
    try:
        width, height = "1080", "1920"
        suffix = "_9x16 Vertical"
        if format == "1:1":
            width, height = "1080", "1080"
            suffix = "_1x1 Square"
            
        name = timeline.GetName() + suffix
        timeline.DuplicateTimeline(name)
        
        t_count = core.project.GetTimelineCount()
        for i in range(1, t_count + 1):
            t = core.project.GetTimelineByIndex(i)
            if t.GetName() == name:
                core.project.SetCurrentTimeline(t)
                t.SetSetting("useCustomSettings", "1")
                t.SetSetting("timelineResolutionWidth", width)
                t.SetSetting("timelineResolutionHeight", height)
                t.SetSetting("timelineInputResMismatchAction", "scaleToCrop")
                
                track_count = t.GetTrackCount("video")
                for track_idx in range(1, track_count + 1):
                    items = t.GetItemListInTrack("video", track_idx)
                    if items:
                        for item in items:
                            item.SetProperty("Scaling", 3)
                            
                return True, f"Created and switched to '{name}' ({format})"
        return False, "Failed to switch to new timeline."
    except Exception as e:
        return False, str(e)

def auto_sync_audio(core):
    """Sync audio for selected Media Pool items based on waveform"""
    try:
        if not core.media_pool:
            return False, "Not connected to Media Pool."
            
        selected_clips = core.media_pool.GetSelectedClips()
        if not selected_clips:
            return False, "Please select at least one video and one audio clip in the Media Pool."
            
        clips_list = []
        if isinstance(selected_clips, dict):
            clips_list = list(selected_clips.values())
        elif isinstance(selected_clips, list):
            clips_list = selected_clips
            
        if len(clips_list) < 2:
            return False, "Need at least 2 clips selected to sync audio."
            
        # 1 = resolve.AUDIO_SYNC_WAVEFORM
        success = core.media_pool.AutoSyncAudio(clips_list, {"audioSyncMode": 1})
        
        if success:
            return True, f"✓ Successfully synced audio for {len(clips_list)} clips based on waveform."
        else:
            return False, "Failed to auto-sync. Ensure clips have matching audio waveforms."
            
    except Exception as e:
        return False, f"Error syncing audio: {str(e)}"
        
def add_quick_title(core, text="New Title"):
    """Add a simple text title at the current playhead"""
    timeline = core.project.GetCurrentTimeline()
    if not timeline:
        return False, "No active timeline"
        
    try:
        item = timeline.InsertTitleIntoTimeline("Text")
        if not item:
            return False, "Failed to insert Title. Is the playhead at a valid point?"
        return True, "Quick Title added at playhead."
    except Exception as e:
        return False, f"Error adding title: {e}"

def add_adjustment_layer(core):
    """Inserts an 'Adjustment Clip' onto Track 5 at playhead without rippling. Requires Media Pool clip."""
    timeline = core.project.GetCurrentTimeline()
    if not timeline:
        return False, "No active timeline"
        
    try:
        import time_parser
        
        adj_clip = core.get_clip_by_name("Adjustment Clip")
        if not adj_clip:
            return False, "Please add an 'Adjustment Clip' to your Media Pool. (Effects insertion cannot target Track 5 or avoid shifting footage)."
            
        fps = float(core.project.GetSetting("timelineFrameRate"))
        tc = timeline.GetCurrentTimecode()
        secs = time_parser.parse_time(tc, fps)
        record_frame = int(round(secs * fps))
        
        # Default duration 5 seconds
        duration = int(fps * 5)
        
        append_info = [{
            "mediaPoolItem": adj_clip,
            "startFrame": 0, 
            "endFrame": duration - 1,
            "trackIndex": 5,
            "recordFrame": record_frame
        }]
        
        res = core.media_pool.AppendToTimeline(append_info)
        if not res:
            return False, "Failed to append to Track 5. Make sure the track exists or can be created."
            
        return True, "Quick Adjustment Layer added at playhead on Track 5."
    except Exception as e:
        return False, f"Error adding Adjustment Layer: {e}"
