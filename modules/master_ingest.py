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
            
    return False, "Could not connect to DaVinci Resolve. Please ensure DaVinci Resolve is open, and close any open dialogs/modal windows (like 'Add Project Library' or 'Preferences') inside Resolve."

def create_master_folder_structure(parent_dir: str, project_name: str, client_name: str = "", project_type: str = "Standard Video") -> tuple[bool, str, str]:
    """
    Creates a Post Haste-style standardized Master Folder structure on disk.
    Returns (success, message, folder_path).
    """
    if not parent_dir or not os.path.exists(parent_dir):
        return False, f"Invalid parent folder path: '{parent_dir}'", ""
    
    clean_proj = project_name.strip() if project_name else "Untitled Project"
    clean_client = client_name.strip() if client_name else ""
    date_str = time.strftime("%Y-%m-%d")
    
    if clean_client:
        folder_name = f"{date_str}_{clean_client}_{clean_proj}"
    else:
        folder_name = f"{date_str}_{clean_proj}"
        
    master_path = os.path.join(parent_dir, folder_name)
    
    # Preset folder hierarchies
    if "Social" in project_type:
        subfolders = [
            os.path.join("Raw Footages", "Card 01"),
            "Davinci Resolve Database",
            "Audio & Music",
            "Graphics & Assets",
            "Exports"
        ]
    elif "Commercial" in project_type:
        subfolders = [
            os.path.join("Raw Footages", "Camera A"),
            os.path.join("Raw Footages", "Camera B"),
            "Davinci Resolve Database",
            "Audio & Voiceover",
            "Motion Graphics",
            "Photoshop",
            "Client Approvals & Exports",
            "Documents"
        ]
    else: # Standard Video & Film
        subfolders = [
            os.path.join("Raw Footages", "Card 01"),
            os.path.join("Raw Footages", "Card 02"),
            "Davinci Resolve Database",
            "BG Music",
            "After Effects",
            "Photoshop",
            "Exports",
            "Production Documents"
        ]
        
    try:
        os.makedirs(master_path, exist_ok=True)
        for sf in subfolders:
            os.makedirs(os.path.join(master_path, sf), exist_ok=True)
        return True, f"✓ Master Folder structure successfully created at: {master_path}", master_path
    except Exception as e:
        return False, f"Failed to create Master Folder: {str(e)}", ""

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
    
    # 1. Project Library (Database) Selection: Check if a database with this name already exists in Resolve
    try:
        db_list = pm.GetDatabaseList() or []
        for db in db_list:
            if isinstance(db, dict) and db.get("DbName") == base_project_name:
                pm.SetCurrentDatabase(db)
                break
    except Exception as e:
        print(f"Notice on Database switch: {e}")

    # 2. Project Creation & Versioning
    existing_projects = pm.GetProjectListInCurrentFolder() or []
    target_project_name = get_versioned_project_name(base_project_name, existing_projects)
    
    project = pm.CreateProject(target_project_name)
    if not project:
        project = pm.LoadProject(target_project_name)
    if not project:
        return False, f"Failed to create/open project: '{target_project_name}'"
    
    core.project = project
    
    # Set Working Folders (Project media location, CacheClip, Gallery) to Master Folder
    try:
        project.SetSetting("projectMediaLocation", master_folder_path)
        cache_dir = os.path.join(master_folder_path, "CacheClip")
        gallery_dir = os.path.join(master_folder_path, ".gallery")
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(gallery_dir, exist_ok=True)
        project.SetSetting("perfCacheClipsLocation", cache_dir)
        project.SetSetting("colorGalleryStillsLocation", gallery_dir)
    except Exception as e:
        print(f"Notice on Working Folders setting: {e}")

    core.media_pool = project.GetMediaPool()
    media_pool = core.media_pool
    if not media_pool:
        return False, "Could not access Media Pool in new project."
    
    root_folder = media_pool.GetRootFolder()
    created_timelines = []
    
    # 3. Create 'Projects' Bin under Master to hold all generated Timelines
    projects_bin = media_pool.AddSubFolder(root_folder, "Projects")
    
    # Check if there is a 'Raw Footages' or 'Footage' folder on disk
    raw_footages_dir = None
    all_subitems = os.listdir(master_folder_path)
    for item in all_subitems:
        full_p = os.path.join(master_folder_path, item)
        if os.path.isdir(full_p) and item.lower() in ["raw footages", "raw footage", "footage", "raw"]:
            raw_footages_dir = full_p
            break
            
    # List of card/footage folders to process: (card_name, folder_path)
    cards_to_process = []
    
    if raw_footages_dir:
        # Create 'Raw Footages' Bin under Master
        raw_bin = media_pool.AddSubFolder(root_folder, "Raw Footages")
        
        # Collect Card 01, Card 02 folders inside Raw Footages
        card_dirs = [f for f in os.listdir(raw_footages_dir) if os.path.isdir(os.path.join(raw_footages_dir, f))]
        for card in sorted(card_dirs):
            if card.lower() not in IGNORED_FOLDERS:
                cards_to_process.append((card, os.path.join(raw_footages_dir, card)))
    else:
        # Create 'Footage' Bin under Master
        raw_bin = media_pool.AddSubFolder(root_folder, "Footage")
        
        # Collect valid subfolders directly from Master Folder
        for item in sorted(all_subitems):
            full_p = os.path.join(master_folder_path, item)
            if os.path.isdir(full_p) and item.lower() not in IGNORED_FOLDERS:
                cards_to_process.append((item, full_p))
                
    # Also check if BG Music / Audio folder exists on disk
    bg_music_dir = None
    for item in all_subitems:
        full_p = os.path.join(master_folder_path, item)
        if os.path.isdir(full_p) and item.lower() in ["bg music", "audio", "music", "sound"]:
            bg_music_dir = (item, full_p)
            break

    # 4. Import Footage & Generate Timelines
    for card_name, folder_path in cards_to_process:
        # Create Card Bin inside Raw Footages Bin
        card_bin = media_pool.AddSubFolder(raw_bin, card_name)
        if card_bin:
            media_pool.SetCurrentFolder(card_bin)
        
        # Collect supported media files recursively inside card folder
        media_files = []
        for r, d, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    media_files.append(os.path.join(r, file))
        
        if media_files:
            imported_items = media_pool.ImportMedia(media_files)
            if imported_items:
                # Switch to Projects Bin to create the Timeline inside Projects Bin!
                if projects_bin:
                    media_pool.SetCurrentFolder(projects_bin)
                
                tl_name = f"{card_name} Timeline"
                tl = media_pool.CreateTimelineFromClips(tl_name, imported_items)
                if tl:
                    created_timelines.append(tl_name)
                    
    # 5. Import BG Music into 'BG Music' Bin under Master (if exists)
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
    
    return True, f"✓ Successfully created project '{target_project_name}' with {len(created_timelines)} Card Timelines inside Projects Bin: {', '.join(created_timelines)}"
