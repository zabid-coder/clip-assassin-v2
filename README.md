# 🎬 Clip Assassin v2.0 - DaVinci Resolve Workflow Automator

**Clip Assassin v2.0** is a powerful automation suite built for **DaVinci Resolve Studio** that acts as your personal assistant editor. What used to be a simple timecode cutter has evolved into a full-fledged Next-Gen Web Application featuring a beautiful modern UI, intelligent batch processing, media organization, social media reframing, and automatic shotlist generation.

---

## ✨ Features

- **Magic Tab** 
  - **Timeline Snapshot:** Save instant backups of your timeline.
  - **Quick Title & Adjustment Layer:** Instantly drop elements at the playhead without diving into the effects library.
- **Destructive Tab** 
  - **Timecode Cutter:** Slice and dice your timeline based on specific timecode ranges (Cut inside or outside).
  - **Clip Picker:** Automatically generate new timelines containing only specific clips.
  - **BadWords Cleaner:** Scan timeline markers for flagged words and ripple-delete them automatically.
  - **Silence Remover:** Detect dead air (silence) on your tracks and ripple-delete it automatically (perfect for jump cuts).
- **Organize & Process Tab**
  - **Magic Bin Organizer:** Automatically sort your Media Pool into Video, Audio, and Image bins.
  - **Multi-Cam Auto Sync:** Select clips in the Media Pool and automatically sync them by audio waveform.
  - **Merge Timelines:** Select multiple timelines and merge them into one master timeline.
  - **Templates/Asset Library:** Drag and drop `.drfx` plugins, images, or audio into the templates folder to import them instantly.
- **Output & Render Tab**
  - **Batch Timeline Render:** Select multiple timelines and send them all to the Render Queue with your chosen preset.
  - **Shotlist Generator:** Automatically generate a detailed Shotlist (CSV or Word Document) directly from your timeline clips.
  - **Social Media Reframe:** Automatically duplicate your timeline and adjust the resolution to 9:16 (Shorts/Reels) or 1:1 (Square) with smart scale-to-crop.
  - **Watermark Track:** Place a watermark logo across the entire video on the top track.

---

## 📋 System Requirements (macOS)

| Requirement | Details |
|---|---|
| **OS** | macOS 12 (Monterey) or later |
| **DaVinci Resolve** | DaVinci Resolve Studio 18 or later *(Scripting API is required, free version has limited support)* |
| **Python** | Python 3.10+ (Recommended to install via Homebrew) |
| **Node.js** | Required for frontend development/building |

### Resolve Configuration
Ensure that **External Scripting** is enabled in Resolve:
`DaVinci Resolve -> Preferences -> System -> General -> External scripting using: Local`

---

## 🚀 One-Click Installation (macOS)

We have simplified the installation process. Just follow these steps on a fresh Mac:

### Step 1: Install Dependencies
Open **Terminal** (`Cmd + Space` -> Terminal) and install Homebrew (if you don't have it):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python and Node.js:
```bash
brew install python@3.12
brew install node
```

### Step 2: Set Up the Project
Open Terminal, navigate to the `Clip_Assassin_Resolve-v2.0.0` folder, and run:

```bash
# 1. Create a Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 2. Install Backend Packages
pip install -r requirements.txt

# 3. Build the Frontend UI
cd frontend
npm install
npm run build
cd ..
```

### Step 3: Run the App
Double-click the **`Run_Clip_Assassin.command`** file in the project folder. 
*(If it says "Permission denied", open Terminal and run `chmod +x Run_Clip_Assassin.command`)*

The backend server will start and automatically open the beautiful web interface in your default browser at `http://127.0.0.1:8000`.

---

## 🛠️ Architecture

Clip Assassin v2.0 has been completely rewritten from its PyQt5 roots into a modern web stack:

- **Backend:** `FastAPI` (Python) - Interfaces with the DaVinci Resolve Python Scripting API via `resolve_core.py`.
- **Frontend:** `React` + `Vite` + `TailwindCSS` - A stunning, glassmorphism-inspired dark mode UI.

### Development Mode
If you want to modify the frontend UI, open two terminal windows:

**Terminal 1 (Backend):**
```bash
source venv/bin/activate
python server.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
Then open `http://localhost:5173` in your browser.

---

## 📜 License
Clip Assassin is provided "as is", without warranty of any kind. Use Timeline Snapshot before running destructive tools!
