# Design Specification: Master Folder Setup & Auto Ingest

**Date:** 2026-07-22  
**Feature:** Master Folder Setup & Auto Ingest  
**Target Platform:** DaVinci Resolve Studio (macOS / Windows)  

---

## 🎯 Purpose & Goal

Automate the tedious initial project setup in DaVinci Resolve Studio by scanning a PC/Mac Master Folder structure. The tool will:
1. Ensure DaVinci Resolve is running (launching it automatically if closed).
2. Create a new DaVinci Resolve Project named after the Master Folder (with smart versioning `_v2`, `_v3` if a project already exists).
3. Mirror the sub-folder structure inside DaVinci's Media Pool as Bins.
4. Import all video/audio assets into their corresponding Bins.
5. Automatically create individual Timelines for each sub-folder populated with its assets.

---

## 🏗️ Architectural Overview

```
[ User UI Input ] (Master Folder Path)
       │
       ▼
[ POST /api/master_ingest ] (FastAPI Endpoint)
       │
       ▼
[ master_ingest.py ] 
  ├── 1. Check & Auto-Launch Resolve (OS Launch + API Retry)
  ├── 2. Determine Project Name & Versioning (ProjectManager API)
  ├── 3. Create & Open New Project
  ├── 4. Traverse Master Folder -> Create Bins & Import Media
  └── 5. Generate Timelines per Sub-Folder
       │
       ▼
[ Response to UI ] (Success Summary & Timelines List)
```

---

## 📦 Component Specifications

### 1. Backend Module (`modules/master_ingest.py`)
- **`ensure_resolve_running(core)`**:
  - Connects to Resolve. If failed, launches Resolve process (`open -a "DaVinci Resolve"` on macOS or `start` on Windows) and polls up to 30 seconds until API responds.
- **`get_versioned_project_name(project_manager, base_name)`**:
  - Fetches existing project list from `project_manager.GetProjectListInCurrentFolder()`.
  - If `base_name` exists, increments suffix to `base_name_v2`, `base_name_v3`, etc.
- **`process_master_ingest(core, master_folder)`**:
  - Ensures Resolve is active and creates the versioned project.
  - Gets `root_bin` from `media_pool.GetRootFolder()`.
  - Scans `master_folder` for immediate sub-directories:
    - Creates a sub-folder bin: `media_pool.AddSubFolder(root_bin, folder_name)`.
    - Collects all media files (`.mp4`, `.mov`, `.mkv`, `.m4v`, `.mp3`, `.wav`, `.aac`, `.braw`, `.arri`, `.png`, `.jpg`).
    - Imports clips: `media_pool.ImportMedia(file_paths)`.
    - Calls `media_pool.CreateTimelineFromClips(f"{folder_name} Timeline", imported_clips)`.
  - Returns tuple `(success: bool, message: str, timeline_count: int)`.

### 2. API Endpoint (`server.py`)
- **Request Model**:
  ```python
  class MasterIngestRequest(BaseModel):
      master_folder_path: str
  ```
- **Endpoint**:
  ```python
  @app.post("/api/master_ingest", response_model=StandardResponse)
  def execute_master_ingest(req: MasterIngestRequest):
      success, msg = engine.run_master_ingest(req.master_folder_path)
      return StandardResponse(success=success, message=msg)
  ```

### 3. Frontend Component (`frontend/src/App.tsx`)
- New Feature Card inside **Organize & Process** tab:
  - Input field for Master Folder Path (with Folder Browser button).
  - "Start Master Ingest" action button with loading spinner.
  - Interactive toast/status message on completion.

---

## 🧪 Verification & Testing Plan

1. **Unit Test / Integration Script (`test_master_ingest.py`)**:
   - Create a dummy test folder structure with mock/sample media on desktop.
   - Run `process_master_ingest` and verify project creation, bin creation, media import, and timeline creation.
2. **Frontend UI Verification**:
   - Verify input fields, browse button, loading state, and backend API trigger.
3. **Full Build Check**:
   - Run `npm run build` in `frontend/` to ensure no TypeScript or CSS errors.
