import logging
import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

# Ensure resolve_core is accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from resolve_core import ResolveConnection
import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("clip_assassin")

app = FastAPI(title="Clip Assassin API", version="2.0.1")

# CORS: only the local dev vite server and the packaged desktop app origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize Resolve engine
engine = ResolveConnection()

# --- Pydantic Models ---

class ConnectResponse(BaseModel):
    success: bool
    message: str

class CutRequest(BaseModel):
    timecodes: str
    reverse: bool = False
    clip_name: Optional[str] = ""

class ClipPickRequest(BaseModel):
    names: str

class MarkerRequest(BaseModel):
    color: str = "All"

class FlagRequest(BaseModel):
    color: str = "Green"

class MergeRequest(BaseModel):
    timeline_names: str

class WatermarkRequest(BaseModel):
    image_path: str

class BatchRenderRequest(BaseModel):
    timelines: List[str]
    target_dir: str
    preset_name: str

class ThumbnailRequest(BaseModel):
    mode: str
    target_dir: str

class ShotlistRequest(BaseModel):
    format: str
    target_path: str
    template_path: Optional[str] = ""

class MasterIngestRequest(BaseModel):
    master_folder_path: str

class CreateMasterFolderRequest(BaseModel):
    parent_dir: str
    project_name: str
    client_name: Optional[str] = ""
    project_type: Optional[str] = "Standard Video"
    custom_date: Optional[str] = ""

class CreateMasterFolderResponse(BaseModel):
    success: bool
    message: str
    folder_path: str

class TemplateImportRequest(BaseModel):
    template_name: str

class SetTimelineRequest(BaseModel):
    timeline_name: str

class SettingRequest(BaseModel):
    key: str
    value: str

class StandardResponse(BaseModel):
    success: bool
    message: str

# --- API Endpoints ---

@app.get("/api/status", response_model=ConnectResponse)
def get_status():
    """Check if Resolve is currently connected"""
    if engine.project and engine.media_pool:
        return ConnectResponse(success=True, message="Connected to DaVinci Resolve")
    return ConnectResponse(success=False, message="Not connected")

@app.post("/api/connect", response_model=ConnectResponse)
def connect_resolve():
    success, msg = engine.connect()
    return ConnectResponse(success=success, message=msg)

@app.get("/api/stats")
def get_stats():
    """Get live timeline stats"""
    return engine.get_timeline_stats()

@app.post("/api/cut", response_model=StandardResponse)
def execute_cut(req: CutRequest):
    success, msg = engine.cut_video(req.timecodes, req.reverse, req.clip_name)
    return StandardResponse(success=success, message=msg)

@app.post("/api/pick_clips", response_model=StandardResponse)
def execute_pick_clips(req: ClipPickRequest):
    success, msg = engine.pick_clips_from_timeline(req.names)
    return StandardResponse(success=success, message=msg)

@app.post("/api/markers_to_timeline", response_model=StandardResponse)
def execute_markers(req: MarkerRequest):
    success, msg = engine.markers_to_timeline(req.color)
    return StandardResponse(success=success, message=msg)

@app.post("/api/filter_by_flag", response_model=StandardResponse)
def execute_flags(req: FlagRequest):
    success, msg = engine.filter_by_flag(req.color)
    return StandardResponse(success=success, message=msg)

@app.post("/api/merge_timelines", response_model=StandardResponse)
def execute_merge(req: MergeRequest):
    success, msg = engine.merge_timelines(req.timeline_names)
    return StandardResponse(success=success, message=msg)

@app.post("/api/apply_watermark", response_model=StandardResponse)
def execute_watermark(req: WatermarkRequest):
    success, msg = engine.apply_watermark_track(req.image_path)
    return StandardResponse(success=success, message=msg)

@app.post("/api/batch_render", response_model=StandardResponse)
def execute_batch_render(req: BatchRenderRequest):
    success, msg = engine.batch_render(req.timelines, req.preset_name, req.target_dir)
    return StandardResponse(success=success, message=msg)

@app.post("/api/extract_thumbnails", response_model=StandardResponse)
def execute_thumbnails(req: ThumbnailRequest):
    success, msg = engine.extract_thumbnails(req.mode, req.target_dir)
    return StandardResponse(success=success, message=msg)



@app.post("/api/youtube_chapters", response_model=StandardResponse)
def execute_yt_chapters():
    success, msg = engine.generate_youtube_chapters()
    return StandardResponse(success=success, message=msg)

@app.post("/api/organize_bins", response_model=StandardResponse)
def execute_organize_bins():
    success, msg = engine.organize_media_pool()
    return StandardResponse(success=success, message=msg)

@app.post("/api/auto_sync", response_model=StandardResponse)
def execute_auto_sync():
    success, msg = engine.auto_sync_audio()
    return StandardResponse(success=success, message=msg)

class SocialReframeRequest(BaseModel):
    format: str = "9:16"

@app.post("/api/social_reframe", response_model=StandardResponse)
def execute_social_reframe(req: SocialReframeRequest):
    success, msg = engine.create_social_timeline(req.format)
    return StandardResponse(success=success, message=msg)

@app.post("/api/add_title", response_model=StandardResponse)
def execute_add_title():
    success, msg = engine.add_quick_title()
    return StandardResponse(success=success, message=msg)

@app.post("/api/add_adjustment_layer", response_model=StandardResponse)
def execute_add_adjustment():
    success, msg = engine.add_adjustment_layer()
    return StandardResponse(success=success, message=msg)

@app.post("/api/export_shotlist", response_model=StandardResponse)
def execute_export_shotlist(req: ShotlistRequest):
    success, msg = engine.export_shotlist_doc(req.format, req.target_path, req.template_path)
    return StandardResponse(success=success, message=msg)

@app.post("/api/master_ingest", response_model=StandardResponse)
def execute_master_ingest(req: MasterIngestRequest):
    success, msg = engine.run_master_ingest(req.master_folder_path)
    return StandardResponse(success=success, message=msg)

@app.post("/api/create_master_folder", response_model=CreateMasterFolderResponse)
def execute_create_master_folder(req: CreateMasterFolderRequest):
    success, msg, folder_path = engine.run_create_master_folder(req.parent_dir, req.project_name, req.client_name, req.project_type, req.custom_date)
    return CreateMasterFolderResponse(success=success, message=msg, folder_path=folder_path)

@app.post("/api/subtitles", response_model=StandardResponse)
def execute_subtitles():
    success, msg = engine.generate_subtitles()
    return StandardResponse(success=success, message=msg)

@app.post("/api/upload_youtube", response_model=StandardResponse)
def execute_upload_youtube():
    success, msg = engine.upload_to_youtube()
    return StandardResponse(success=success, message=msg)

@app.get("/api/templates")
def get_templates():
    return engine.get_templates()

@app.post("/api/import_template", response_model=StandardResponse)
def execute_import_template(req: TemplateImportRequest):
    success, msg = engine.import_template(req.template_name)
    return StandardResponse(success=success, message=msg)

@app.get("/api/context")
def get_global_context():
    return engine.get_global_context()

@app.post("/api/set_context", response_model=StandardResponse)
def execute_set_context(req: SetTimelineRequest):
    success, msg = engine.set_active_timeline(req.timeline_name)
    return StandardResponse(success=success, message=msg)

@app.get("/api/settings")
def get_settings():
    return {"success": True, "settings": db.get_all_settings()}

import subprocess
import platform

@app.get("/api/browse")
def browse_path(type: str = "file"):
    """Open a native file/folder picker dialog and return the selected path."""
    try:
        if platform.system() == "Darwin":
            if type == "folder":
                script = 'POSIX path of (choose folder with prompt "Select Folder")'
            elif type == "save":
                script = 'POSIX path of (choose file name with prompt "Save As...")'
            else:
                script = 'POSIX path of (choose file with prompt "Select File")'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "path": result.stdout.strip()}
            return {"success": False, "error": "Cancelled"}

        elif platform.system() == "Windows":
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            if type == "folder":
                path = filedialog.askdirectory(title="Select Folder")
            elif type == "save":
                path = filedialog.asksaveasfilename(title="Save As...")
            else:
                path = filedialog.askopenfilename(title="Select File")
            root.destroy()
            if path:
                return {"success": True, "path": path}
            return {"success": False, "error": "Cancelled"}

        else:
            return {"success": False, "error": f"File dialog not supported on {platform.system()}"}
    except Exception as e:
        logger.error(f"Browse dialog error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/open_folder")
def open_folder(path: str):
    """Open a folder in the system file manager with path validation."""
    try:
        full_path = os.path.abspath(path)

        # Security: reject path traversal attempts
        if ".." in path:
            logger.warning(f"Path traversal attempt blocked: {path}")
            return {"success": False, "error": "Invalid path"}

        if not os.path.isdir(full_path):
            return {"success": False, "error": "Folder not found"}

        if platform.system() == "Darwin":
            subprocess.run(['open', full_path])
        elif platform.system() == "Windows":
            subprocess.run(['explorer', full_path])
        else:
            subprocess.run(['xdg-open', full_path])

        return {"success": True}
    except Exception as e:
        logger.error(f"Open folder error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/settings", response_model=StandardResponse)
def save_setting(req: SettingRequest):
    db.set_setting(req.key, req.value)
    return StandardResponse(success=True, message="Setting saved")

# --- BadWords Integration ---

class BadWordsCleanRequest(BaseModel):
    colors: List[str]

@app.get("/api/badwords/scan")
def scan_badwords_markers():
    return engine.scan_badwords_markers()

@app.post("/api/badwords/clean", response_model=StandardResponse)
def clean_badwords_timeline(req: BadWordsCleanRequest):
    success, msg = engine.clean_badwords_timeline(req.colors)
    return StandardResponse(success=success, message=msg)

# --- Utility Tools ---

class RenameRequest(BaseModel):
    prefix: str
    start_number: int = 1
    scope: str = "timeline"

class SilenceRequest(BaseModel):
    threshold_db: int = -40
    min_silence_ms: int = 500
    padding_ms: int = 100

class JLCutRequest(BaseModel):
    cut_type: str = "j"
    overlap_frames: int = 10

@app.post("/api/snapshot", response_model=StandardResponse)
def create_snapshot():
    success, msg = engine.create_snapshot()
    return StandardResponse(success=success, message=msg)

@app.post("/api/batch_rename", response_model=StandardResponse)
def batch_rename(req: RenameRequest):
    success, msg = engine.batch_rename_clips(req.prefix, req.start_number, req.scope)
    return StandardResponse(success=success, message=msg)

@app.get("/api/project_stats")
def get_project_stats():
    return engine.get_project_stats_detail()

@app.post("/api/jl_cut", response_model=StandardResponse)
def apply_jl_cuts(req: JLCutRequest):
    success, msg = engine.apply_jl_cuts(req.cut_type, req.overlap_frames)
    return StandardResponse(success=success, message=msg)

@app.get("/api/render_status")
def get_render_status():
    return engine.get_render_status()

@app.post("/api/silence_remove", response_model=StandardResponse)
def detect_silence(req: SilenceRequest):
    success, msg = engine.detect_silence(req.threshold_db, req.min_silence_ms, req.padding_ms)
    return StandardResponse(success=success, message=msg)

class PresetRequest(BaseModel):
    name: str
    data: dict

@app.get("/api/presets")
def get_presets():
    return {"success": True, "presets": db.get_all_presets()}

@app.post("/api/presets", response_model=StandardResponse)
def save_preset(req: PresetRequest):
    db.save_preset(req.name, req.data)
    return StandardResponse(success=True, message="Preset saved")

@app.delete("/api/presets/{preset_id}", response_model=StandardResponse)
def delete_preset(preset_id: int):
    db.delete_preset(preset_id)
    return StandardResponse(success=True, message="Preset deleted")

# PyInstaller compatibility for file paths
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Serve the static React frontend
frontend_dist = os.path.join(base_dir, "frontend", "dist")

if os.path.isdir(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        # Serve static files if they exist (e.g., /logo.jpg, /favicon.ico)
        file_path = os.path.join(frontend_dist, catchall)
        no_cache_headers = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"}
        if os.path.isfile(file_path):
            return FileResponse(file_path, headers=no_cache_headers)
        # Fallback to index.html for client-side routing
        return FileResponse(os.path.join(frontend_dist, "index.html"), headers=no_cache_headers)
else:
    print(f"Warning: Frontend build directory not found at {frontend_dist}. Please run 'npm run build' in the frontend folder.")

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    from threading import Timer
    
    is_prod = getattr(sys, 'frozen', False)
    
    if is_prod:
        # In production (packaged), open the browser automatically
        Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
        # Must pass 'app' instance, not string, when not using reload
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
    else:
        # In development, use reload
        uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)


# ==================== TEMPLATE API ENDPOINTS ====================

class TemplateCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    category: str = "Custom"
    structure: List[Dict[str, Any]]
    parameters: List[Dict[str, Any]]
    placeholders: Dict[str, str] = {}

class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    structure: Optional[List[Dict[str, Any]]] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    placeholders: Optional[Dict[str, str]] = None

class TemplateParamRequest(BaseModel):
    param_values: Dict[str, Any]

@app.get("/api/templates/builtin")
def get_builtin_templates_api():
    """Get all built-in templates"""
    from modules.master_ingest import get_builtin_templates
    templates = get_builtin_templates()
    return {"success": True, "templates": templates}

@app.get("/api/templates")
def get_all_templates(include_builtin: bool = False):
    """Get all user-created templates (optionally include built-in)"""
    templates = template_db.get_all_templates(include_builtin=include_builtin)
    return {"success": True, "templates": templates}

@app.get("/api/templates/{template_id}")
def get_template(template_id: int):
    """Get a single template by ID"""
    template = template_db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"success": True, "template": template}

@app.post("/api/templates", response_model=StandardResponse)
def create_template(req: TemplateCreateRequest):
    """Create a new template"""
    try:
        template_id = template_db.create_template(
            name=req.name,
            description=req.description,
            category=req.category,
            structure=req.structure,
            parameters=req.parameters,
            placeholders=req.placeholders,
            is_builtin=0
        )
        return StandardResponse(success=True, message=f"Template created with ID {template_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/templates/{template_id}", response_model=StandardResponse)
def update_template(template_id: int, req: TemplateUpdateRequest):
    """Update an existing template"""
    success = template_db.update_template(
        template_id=template_id,
        name=req.name,
        description=req.description,
        category=req.category,
        structure=req.structure,
        parameters=req.parameters,
        placeholders=req.placeholders
    )
    if success:
        return StandardResponse(success=True, message="Template updated")
    else:
        raise HTTPException(status_code=400, detail="Failed to update template or template is builtin")

@app.delete("/api/templates/{template_id}", response_model=StandardResponse)
def delete_template(template_id: int):
    """Delete a template (cannot delete built-in)"""
    success = template_db.delete_template(template_id)
    if success:
        return StandardResponse(success=True, message="Template deleted")
    else:
        raise HTTPException(status_code=400, detail="Failed to delete template or template is builtin")

@app.post("/api/templates/{template_id}/preview")
def preview_template_structure(template_id: int, req: TemplateParamRequest):
    """Preview what folder structure will be created without actually creating it"""
    from modules.master_ingest import resolve_variables
    
    template = template_db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Merge defaults with provided values
    all_params = {}
    for param in template["parameters"]:
        default = param.get("default", "")
        if default == "{today}" or default == "{date}":
            from datetime import datetime
            default = datetime.now().strftime("%Y-%m-%d")
        all_params[param["name"]] = default
    all_params.update(req.param_values)
    
    # Generate preview structure (simplified representation)
    def build_preview(elements, indent=0):
        preview = []
        for elem in elements:
            elem_type = elem.get("type", "folder")
            name = resolve_variables(elem.get("name", ""), all_params)
            
            if elem_type == "folder":
                preview.append(("📁 " + "  " * indent + name, "folder"))
                children = elem.get("children", [])
                preview.extend(build_preview(children, indent + 1))
            elif elem_type == "file":
                preview.append(("📄 " + "  " * indent + name, "file"))
            elif elem_type == "loop":
                var_name = elem.get("var", "i")
                start = int(resolve_variables(str(elem.get("start", 1)), all_params))
                end_str = resolve_variables(str(elem.get("end", 1)), all_params)
                try:
                    end = int(end_str)
                except:
                    end = start
                
                template_elem = elem.get("template", {})
                for i in range(start, min(end + 1, start + 10)):  # Limit preview to 10 items
                    loop_params = all_params.copy()
                    loop_params[var_name] = i
                    loop_name = resolve_variables(template_elem.get("name", ""), loop_params)
                    preview.append(("📁 " + "  " * indent + loop_name + " (loop)", "folder"))
        
        return preview
    
    preview_items = build_preview(template["structure"])
    return {
        "success": True,
        "preview": [{"name": item[0], "type": item[1]} for item in preview_items],
        "params_used": all_params
    }

@app.post("/api/ingest/from-template", response_model=CreateMasterFolderResponse)
def create_folder_from_template(req: TemplateParamRequest):
    """Create master folder structure from a template"""
    from modules.master_ingest import create_master_folder_from_template
    
    # Get template_id from request (need to add to model)
    template_id = getattr(req, 'template_id', None)
    parent_dir = getattr(req, 'parent_dir', None)
    
    if not template_id or not parent_dir:
        raise HTTPException(status_code=400, detail="template_id and parent_dir required")
    
    success, msg, folder_path = create_master_folder_from_template(
        template_id, parent_dir, req.param_values
    )
    
    return CreateMasterFolderResponse(
        success=success,
        message=msg,
        folder_path=folder_path
    )

# Preset endpoints
class PresetCreateRequest(BaseModel):
    name: str
    template_id: int
    param_values: Dict[str, Any]

@app.get("/api/presets/template/{template_id}")
def get_presets_for_template(template_id: int):
    """Get all presets for a template"""
    presets = template_db.get_presets_for_template(template_id)
    return {"success": True, "presets": presets}

@app.post("/api/presets", response_model=StandardResponse)
def create_preset(req: PresetCreateRequest):
    """Create a new preset"""
    preset_id = template_db.create_preset(req.name, req.template_id, req.param_values)
    return StandardResponse(success=True, message=f"Preset created with ID {preset_id}")

@app.delete("/api/presets/{preset_id}", response_model=StandardResponse)
def delete_preset(preset_id: int):
    """Delete a preset"""
    template_db.delete_preset(preset_id)
    return StandardResponse(success=True, message="Preset deleted")

