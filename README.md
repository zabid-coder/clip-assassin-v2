# 🎬 Clip Assassin v2.0.1 — DaVinci Resolve Workflow Automator

![Clip Assassin Version](https://img.shields.io/badge/version-2.0.1-purple.svg)
![DaVinci Resolve Studio](https://img.shields.io/badge/DaVinci_Resolve-Studio_18_|_19_|_21-orange.svg)
![Platform](https://img.shields.io/badge/platform-macOS_|_Windows-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Clip Assassin v2.0.1** is a high-performance, next-generation automation suite and assistant editor built specifically for **DaVinci Resolve Studio** (macOS & Windows). 

Powered by a modern **React 18 + FastAPI** architecture, Clip Assassin eliminates hours of repetitive post-production work — from 1-click project initialization and card ingesting to frame-accurate timecode cutting, silence removal, social media reframing, and batch timeline rendering.

---

## ✨ Feature Overview

### 📁 1. Master Ingest & Auto Project Setup (NEW in v2.0.1)
- **1-Click Master Ingest:** Select your project's Master Folder on Mac/PC and click *Start Master Ingest*.
- **Auto Resolve Launcher:** Automatically activates or launches DaVinci Resolve if it isn't open.
- **Smart Project & Library Creation:** Automatically creates a DaVinci Resolve project named after your Master Folder (with smart versioning `ProjectName_v2`, `_v3` if a project already exists).
- **Automated Bin Hierarchy:** Scans `Raw Footages` in your Master Folder and creates matching sub-bins (`Card 01`, `Card 02`) inside `Master / Raw Footages`.
- **Card Timelines in Projects Bin:** Generates individual timelines for each camera card (e.g. `Card 01 Timeline`) and places them neatly inside a dedicated `Master / Projects` Bin.
- **Automatic Working Folders Configuration:** Automatically configures DaVinci Resolve's `Project media location`, `CacheClip`, and `.gallery` paths directly to your Master Folder location, keeping all render cache and stills organized per project.

---

### 🪄 2. Magic Tools & Reframing
- **Timeline Snapshot:** Create instant non-destructive backups of your active timeline before executing major edits.
- **Social Media Reframe:** 1-click reframing of horizontal timelines into **9:16 Vertical** (Shorts/Reels) or **1:1 Square** format with automatic scale-to-fill crop and `_9x16` / `_Square` naming conventions.
- **Batch Clip Renamer:** Renames every clip on Video Track 1 sequentially using custom project prefixes.
- **Quick Title & Adjustment Layer:** Instantly inserts titles or adjustment clips on Track 5 at the playhead position without opening effects menus.
- **Multi-Cam Auto Sync:** Automatically synchronizes selected Media Pool clips by audio waveform matching.

---

### ✂️ 3. Cut & Trim Tools
- **Frame-Accurate Timecode Cutter:** Slices timeline footage using professional timecode formats (`HH:MM:SS:FF` for non-drop frame or `HH:MM:SS;FF` for drop-frame), supporting 23.976, 24, 25, 29.97, 30, 50, 59.94, and 60 fps.
- **REVERSE BLADES Mode:** Slices and keeps everything *outside* specified ranges (ideal for removing ads, intros, or unwanted segments).
- **Silence Remover:** Detects dead air on audio/video tracks and ripple-deletes silences automatically.
- **BadWords Cleaner:** Scans timeline markers for flagged words and ripple-deletes marked sections.
- **Clip Picker & Marker Filters:** Pulls specific clip numbers or marker/flag colors into dedicated edit timelines.

---

### 🔄 4. Organization & Process Automation
- **Magic Bin Organizer:** Automatically sorts unsorted Media Pool items into clean `Video`, `Audio`, and `Image` bins.
- **Merge Timelines:** Merges multiple selected timelines into one master timeline in sequential order.
- **Watermark Track:** Places logo watermarks across the top video track of the entire video.
- **Auto J-Cut / L-Cut:** Automatically offsets audio cut points to create professional interview split edits.
- **Asset Library:** Imports `.drfx` templates, graphics, and music plugins directly into your project Media Pool.

---

### 📤 5. Export & Batch Processing
- **Batch Timeline Render:** Select multiple timelines across your project and add them all to the Render Queue with custom Resolve presets.
- **Extract Still Frames:** Saves still frames at every timeline marker or selection into a designated export directory.
- **Auto YouTube Chapters:** Generates formatted, timestamped chapter descriptions directly from timeline markers.
- **Client Shotlist Exporter:** Exports clip metadata and shot lists as structured CSV or document files for client review.

---

## 📋 System Requirements & Setup

| Requirement | Specification |
|---|---|
| **OS** | macOS 12+ (Monterey, Ventura, Sonoma, Sequoia) or Windows 10/11 |
| **DaVinci Resolve** | **DaVinci Resolve Studio 18, 19, or 21** |
| **Python** | Python 3.10+ |
| **Node.js** | Node.js 18+ (Required for frontend build) |

### ⚙️ DaVinci Resolve Preferences Requirement
Before using Clip Assassin, make sure **External Scripting** is enabled in DaVinci Resolve:
1. Open **DaVinci Resolve**.
2. Go to **Preferences -> System -> General**.
3. Set **External scripting using** to **Local**.
4. Click **Save**.

---

## 🚀 Quick Start & Installation

### macOS
1. Open **Terminal** inside the project folder:
```bash
# 1. Create Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 2. Install Python Dependencies
pip install -r requirements.txt

# 3. Build Web Interface
cd frontend
npm install
npm run build
cd ..
```
2. Double-click **`Run_Clip_Assassin.command`** (or run `./Run_Clip_Assassin.command` in Terminal).
3. Clip Assassin will start the local server and open `http://127.0.0.1:8000` in your default browser.

### Windows
1. Double-click **`INSTALL.bat`** to automatically set up the virtual environment, install dependencies, and build the frontend.
2. Double-click **`RUN_CLIP_ASSASSIN.bat`** to launch Clip Assassin on Windows.

---

## 🛠️ Architecture Overview

- **Backend:** `FastAPI` (Python 3) — Handles asynchronous REST endpoints, timeline processing, and IPC communication via `resolve_core.py`.
- **Frontend:** `React 18` + `Vite` + `TailwindCSS` — Premium dark-mode interface featuring glassmorphism design tokens, real-time connection status monitoring, and command palette navigation (`Cmd+K`).
- **Resolve API Bridge:** `resolve_core.py` — Integrates with Blackmagic Design's official `DaVinciResolveScript` Python module.

---

## 📜 License & Safety

Clip Assassin is open-source software provided under the MIT License.
*Tip: Always run **Timeline Snapshot** before running destructive trim operations!*
