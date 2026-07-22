# Master Ingest Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a dedicated "Master Ingest" tab and backend pipeline to automatically launch Resolve, create versioned projects, import folder media into Bins, and generate Timelines per folder.

**Architecture:** A Python backend module (`modules/master_ingest.py`) called via FastAPI (`server.py`), triggered from a dedicated React tab (`frontend/src/App.tsx` & `Sidebar.tsx`).

**Tech Stack:** Python 3.12, FastAPI, DaVinci Resolve Python Scripting API, React 18, TailwindCSS.

## Global Constraints

- Must support macOS (`open -a "DaVinci Resolve"`) and Windows (`os.startfile`).
- Must version existing projects with `_v2`, `_v3`, etc.
- Must create Media Pool Bins mirroring Master Folder sub-folders.
- Must create a Timeline per sub-folder populated with its media.
- Must have a dedicated sidebar tab named "Master Ingest".

---

### Task 1: Backend Master Ingest Module

**Files:**
- Create: `modules/master_ingest.py`
- Test: `test_master_ingest.py`
- Modify: `resolve_core.py`

**Interfaces:**
- Consumes: `ResolveConnection` in `resolve_core.py`
- Produces: `run_master_ingest(master_folder_path: str) -> tuple[bool, str]`

- [ ] **Step 1: Write the backend unit test `test_master_ingest.py`**

```python
import os
import sys
import shutil
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.master_ingest import get_versioned_project_name

def test_get_versioned_project_name():
    existing = ["ProjectA", "Wedding_v1", "Wedding_v2"]
    assert get_versioned_project_name("ProjectA", existing) == "ProjectA_v2"
    assert get_versioned_project_name("Wedding", existing) == "Wedding_v3"
    assert get_versioned_project_name("NewProject", existing) == "NewProject"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest test_master_ingest.py`
Expected: FAIL with ModuleNotFoundError or NameError.

- [ ] **Step 3: Implement `modules/master_ingest.py`**

```python
import os
import sys
import time
import subprocess
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".m4v", ".avi", ".braw", ".arri",
    ".mp3", ".wav", ".aac", ".m4a",
    ".png", ".jpg", ".jpeg", ".tiff"
}

def get_versioned_project_name(base_name: str, existing_projects: list[str]) -> str:
    if base_name not in existing_projects:
        return base_name
    
    version = 2
    while f"{base_name}_v{version}" in existing_projects:
        version += 1
    return f"{base_name}_v{version}"

def ensure_resolve_running(core) -> tuple[bool, str]:
    success, msg = core.connect()
    if success:
        return True, "Connected to Resolve"
    
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
    
    # Wait for API up to 25s
    for _ in range(25):
        time.sleep(1)
        success, msg = core.connect()
        if success:
            return True, "Resolve started and connected."
            
    return False, "Timed out waiting for DaVinci Resolve to launch."

def process_master_ingest(core, master_folder_path: str) -> tuple[bool, str]:
    if not os.path.isdir(master_folder_path):
        return False, f"Invalid master folder path: {master_folder_path}"
    
    connected, conn_msg = ensure_resolve_running(core)
    if not connected:
        return False, conn_msg
    
    pm = core.project_manager
    if not pm:
        return False, "Could not access Project Manager"
    
    base_project_name = os.path.basename(os.path.normpath(master_folder_path))
    existing_projects = pm.GetProjectListInCurrentFolder() or []
    target_project_name = get_versioned_project_name(base_project_name, existing_projects)
    
    project = pm.CreateProject(target_project_name)
    if not project:
        project = pm.LoadProject(target_project_name)
    if not project:
        return False, f"Failed to create/open project: {target_project_name}"
    
    core.project = project
    core.media_pool = project.GetMediaPool()
    media_pool = core.media_pool
    root_folder = media_pool.GetRootFolder()
    
    created_timelines = []
    subfolders = [f for f in os.listdir(master_folder_path) if os.path.isdir(os.path.join(master_folder_path, f))]
    
    for sub in subfolders:
        sub_path = os.path.join(master_folder_path, sub)
        sub_bin = media_pool.AddSubFolder(root_folder, sub)
        media_pool.SetCurrentFolder(sub_bin)
        
        # Collect files
        media_files = []
        for r, d, files in os.walk(sub_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    media_files.append(os.path.join(r, file))
        
        if media_files:
            items = media_pool.ImportMedia(media_files)
            if items:
                tl_name = f"{sub} Timeline"
                tl = media_pool.CreateTimelineFromClips(tl_name, items)
                if tl:
                    created_timelines.append(tl_name)
    
    return True, f"Successfully created project '{target_project_name}' with {len(created_timelines)} timelines: {', '.join(created_timelines)}"
```

- [ ] **Step 4: Run pytest to verify it passes**

Run: `pytest test_master_ingest.py`
Expected: PASS

- [ ] **Step 5: Register `run_master_ingest` in `resolve_core.py`**

Modify `resolve_core.py`:
```python
    def run_master_ingest(self, master_folder_path: str):
        from modules import master_ingest
        return master_ingest.process_master_ingest(self, master_folder_path)
```

- [ ] **Step 6: Commit Task 1**

```bash
git add modules/master_ingest.py test_master_ingest.py resolve_core.py
git commit -m "feat: implement backend master ingest module"
```

---

### Task 2: FastAPI API Endpoint

**Files:**
- Modify: `server.py`

**Interfaces:**
- Consumes: `engine.run_master_ingest(master_folder_path)`
- Produces: `POST /api/master_ingest` endpoint

- [ ] **Step 1: Add `MasterIngestRequest` model & `@app.post("/api/master_ingest")` route in `server.py`**

Modify `server.py`:
```python
class MasterIngestRequest(BaseModel):
    master_folder_path: str

@app.post("/api/master_ingest", response_model=StandardResponse)
def execute_master_ingest(req: MasterIngestRequest):
    success, msg = engine.run_master_ingest(req.master_folder_path)
    return StandardResponse(success=success, message=msg)
```

- [ ] **Step 2: Commit Task 2**

```bash
git add server.py
git commit -m "feat: add /api/master_ingest endpoint to FastAPI server"
```

---

### Task 3: Dedicated Frontend Sidebar Tab & UI Component

**Files:**
- Modify: `frontend/src/components/layout/Sidebar.tsx`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `POST /api/master_ingest`
- Produces: Dedicated "Master Ingest" tab view in UI

- [ ] **Step 1: Add "Master Ingest" tab option to `Sidebar.tsx`**

Modify `Sidebar.tsx` tabs list to include:
```typescript
{ id: 'master_ingest', label: 'Master Ingest', icon: 'FolderPlus' }
```

- [ ] **Step 2: Add Master Ingest UI view in `App.tsx`**

Add activeTab handler for `master_ingest` with:
- FeatureCard titled "Master Folder Auto Setup"
- InputField with browseType="folder" ID `masterFolderInput`
- ActionButton `Start Master Ingest` calling `/api/master_ingest`
- Real-time notification and status log feedback.

- [ ] **Step 3: Test frontend build**

Run: `cd frontend && npm run build`
Expected: Clean build without TypeScript or JSX errors.

- [ ] **Step 4: Commit Task 3**

```bash
git add frontend/src/components/layout/Sidebar.tsx frontend/src/App.tsx
git commit -m "feat: add dedicated Master Ingest sidebar tab and UI"
```

---

### Task 4: Integration Verification & Full Audit

**Files:**
- Audit: All files in `frontend/` and `modules/`

- [ ] **Step 1: Run full frontend build**

Run: `cd frontend && npm run build`
Expected: PASS

- [ ] **Step 2: Run all python unit tests**

Run: `pytest`
Expected: PASS

- [ ] **Step 3: Commit Task 4**

```bash
git add .
git commit -m "chore: complete full app audit and master ingest integration"
```
