import os
import sys
import time
import subprocess

SUPPORTED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".m4v", ".avi", ".braw", ".arri",
    ".mp3", ".wav", ".aac", ".m4a",
    ".png", ".jpg", ".jpeg", ".tiff"
}

IGNORED_FOLDERS = {
    "davinci resolve database", "davinci database", "database",
    "after effects", "fcpx", "illustrator", "photoshop", "premiere",
    "export", "exports", "production documents", "documents",
    ".ds_store", "__macosx", ".git", ".idea"
}

def get_versioned_project_name(base_name: str, existing_projects: list[str]) -> str:
    has_match = any(p == base_name or p.startswith(f"{base_name}_v") for p in existing_projects)
    if not has_match:
        return base_name
    
    version = 2
    while f"{base_name}_v{version}" in existing_projects or (version == 1 and base_name in existing_projects):
        version += 1
    return f"{base_name}_v{version}"

def ensure_resolve_running(core) -> tuple[bool, str]:
    success, msg = core.connect()
    if success:
        return True, "Connected to DaVinci Resolve."
    
    # Attempt OS launch using AppleScript to bypass macOS LaunchServices error -54
    try:
        if sys.platform == "darwin":
            res = subprocess.run(["osascript", "-e", 'tell application "DaVinci Resolve" to activate'], capture_output=True)
            if res.returncode != 0:
                res2 = subprocess.run(["osascript", "-e", 'tell application "DaVinci Resolve Studio" to activate'], capture_output=True)
                if res2.returncode != 0:
                    subprocess.Popen(["open", "-a", "DaVinci Resolve"])
        elif sys.platform == "win32":
            win_paths = [
                r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
            ]
            launched = False
            for p in win_paths:
                if os.path.exists(p):
                    subprocess.Popen([p])
                    launched = True
                    break
            if not launched:
                os.system('start "" "DaVinci Resolve"')
        else:
            subprocess.Popen(["resolve"])
    except Exception as e:
        return False, f"Failed to launch Resolve: {str(e)}"
    
    # Poll for connection up to 35s
    for _ in range(35):
        time.sleep(1)
        success, msg = core.connect()
        if success:
            return True, "Resolve started and connected successfully."
            
    return False, "Timed out waiting for DaVinci Resolve to start. Please open DaVinci Resolve on your Mac and try again."

def process_master_ingest(core, master_folder_path: str) -> tuple[bool, str]:
    if not master_folder_path or not os.path.isdir(master_folder_path):
        return False, f"Invalid master folder path: '{master_folder_path}'"
    
    connected, conn_msg = ensure_resolve_running(core)
    if not connected:
        return False, conn_msg
    
    pm = core.project_manager
    if not pm:
        return False, "Could not access Resolve Project Manager."
    
    base_project_name = os.path.basename(os.path.normpath(master_folder_path))
    existing_projects = pm.GetProjectListInCurrentFolder() or []
    target_project_name = get_versioned_project_name(base_project_name, existing_projects)
    
    project = pm.CreateProject(target_project_name)
    if not project:
        project = pm.LoadProject(target_project_name)
    if not project:
        return False, f"Failed to create/open project: '{target_project_name}'"
    
    core.project = project
    core.media_pool = project.GetMediaPool()
    media_pool = core.media_pool
    if not media_pool:
        return False, "Could not access Media Pool in new project."
    
    root_folder = media_pool.GetRootFolder()
    created_timelines = []
    
    # Check if there is a 'Raw Footages' or 'Footage' folder
    raw_footages_dir = None
    all_subitems = os.listdir(master_folder_path)
    for item in all_subitems:
        full_p = os.path.join(master_folder_path, item)
        if os.path.isdir(full_p) and item.lower() in ["raw footages", "raw footage", "footage", "raw"]:
            raw_footages_dir = full_p
            break
            
    # List of card/footage folders to process: (bin_name, folder_path)
    folders_to_process = []
    
    if raw_footages_dir:
        # Process cards inside Raw Footages
        card_dirs = [f for f in os.listdir(raw_footages_dir) if os.path.isdir(os.path.join(raw_footages_dir, f))]
        for card in sorted(card_dirs):
            if card.lower() not in IGNORED_FOLDERS:
                folders_to_process.append((card, os.path.join(raw_footages_dir, card)))
    else:
        # Process direct subfolders of Master Folder, ignoring non-media folders
        for item in sorted(all_subitems):
            full_p = os.path.join(master_folder_path, item)
            if os.path.isdir(full_p) and item.lower() not in IGNORED_FOLDERS:
                folders_to_process.append((item, full_p))
                
    # Also check if BG Music or Audio folder exists to import as Bin
    bg_music_dir = None
    for item in all_subitems:
        full_p = os.path.join(master_folder_path, item)
        if os.path.isdir(full_p) and item.lower() in ["bg music", "audio", "music", "sound"]:
            bg_music_dir = (item, full_p)
            break

    # Process Card / Footage Folders -> Bins + Timelines
    for bin_name, folder_path in folders_to_process:
        sub_bin = media_pool.AddSubFolder(root_folder, bin_name)
        if sub_bin:
            media_pool.SetCurrentFolder(sub_bin)
        
        # Recursively collect all supported media files inside card folder (ignoring 'private' name for timeline!)
        media_files = []
        for r, d, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    media_files.append(os.path.join(r, file))
        
        if media_files:
            imported_items = media_pool.ImportMedia(media_files)
            if imported_items:
                tl_name = f"{bin_name} Timeline"
                tl = media_pool.CreateTimelineFromClips(tl_name, imported_items)
                if tl:
                    created_timelines.append(tl_name)
                    
    # Process BG Music if found -> Bin only
    if bg_music_dir:
        b_name, b_path = bg_music_dir
        music_bin = media_pool.AddSubFolder(root_folder, b_name)
        if music_bin:
            media_pool.SetCurrentFolder(music_bin)
            m_files = []
            for r, d, files in os.walk(b_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        m_files.append(os.path.join(r, file))
            if m_files:
                media_pool.ImportMedia(m_files)
    
    return True, f"✓ Successfully created project '{target_project_name}' with {len(created_timelines)} Card Timelines: {', '.join(created_timelines)}"
