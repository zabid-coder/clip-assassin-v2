import os
import sys
import time
import subprocess

SUPPORTED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".m4v", ".avi", ".braw", ".arri",
    ".mp3", ".wav", ".aac", ".m4a",
    ".png", ".jpg", ".jpeg", ".tiff"
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
    
    # Attempt OS launch
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "DaVinci Resolve"])
        elif sys.platform == "win32":
            os.system('start "" "DaVinci Resolve"')
        else:
            subprocess.Popen(["resolve"])
    except Exception as e:
        return False, f"Failed to launch Resolve: {str(e)}"
    
    # Poll for connection up to 25s
    for _ in range(25):
        time.sleep(1)
        success, msg = core.connect()
        if success:
            return True, "Resolve started and connected successfully."
            
    return False, "Timed out waiting for DaVinci Resolve to start."

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
    
    try:
        subfolders = [f for f in os.listdir(master_folder_path) if os.path.isdir(os.path.join(master_folder_path, f))]
    except Exception as e:
        return False, f"Error reading master folder: {str(e)}"
    
    if not subfolders:
        # If no subfolders, use the master folder itself
        subfolders = ["Footage"]
        master_has_subfolders = False
    else:
        master_has_subfolders = True

    for sub in sorted(subfolders):
        if master_has_subfolders:
            sub_path = os.path.join(master_folder_path, sub)
        else:
            sub_path = master_folder_path
            
        sub_bin = media_pool.AddSubFolder(root_folder, sub)
        if sub_bin:
            media_pool.SetCurrentFolder(sub_bin)
        
        # Collect supported media files
        media_files = []
        for r, d, files in os.walk(sub_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    media_files.append(os.path.join(r, file))
        
        if media_files:
            imported_items = media_pool.ImportMedia(media_files)
            if imported_items:
                tl_name = f"{sub} Timeline"
                tl = media_pool.CreateTimelineFromClips(tl_name, imported_items)
                if tl:
                    created_timelines.append(tl_name)
    
    return True, f"✓ Created project '{target_project_name}' with {len(created_timelines)} timelines ({', '.join(created_timelines)})"
