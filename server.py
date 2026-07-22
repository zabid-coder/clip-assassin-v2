from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure resolve_core is accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from resolve_core import ResolveConnection
import db

app = FastAPI(title="Clip Assassin API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev (e.g. http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
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

@app.get("/api/browse")
def browse_path(type: str = "file"):
    try:
        script = ""
        if type == "folder":
            script = 'POSIX path of (choose folder with prompt "Select Folder")'
        elif type == "save":
            script = 'POSIX path of (choose file name with prompt "Save As...")'
        else:
            script = 'POSIX path of (choose file with prompt "Select File")'
            
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "path": result.stdout.strip()}
        else:
            return {"success": False, "error": "Cancelled"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/open_folder")
def open_folder(path: str):
    import os
    try:
        # Resolve path relative to app root
        full_path = os.path.abspath(path)
        if os.path.exists(full_path):
            subprocess.run(['open', full_path])
            return {"success": True}
        else:
            return {"success": False, "error": "Folder not found"}
    except Exception as e:
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
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback to index.html for client-side routing
        return FileResponse(os.path.join(frontend_dist, "index.html"))
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
