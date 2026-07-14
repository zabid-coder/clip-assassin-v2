# Clip Assassin v2.0 - Installation Guide

This guide provides step-by-step instructions on how to install and run **Clip Assassin v2.0** on a completely new PC for Windows, Mac, and Linux.

---

## 1. Prerequisites (For All OS)

Before running the application, you need to have the following installed on your PC:

1. **DaVinci Resolve Studio (18 or newer)** 
   - *Note: Scripting API is only fully supported in the Studio version.*
   - Ensure that **External Scripting** is enabled in Resolve: 
     `Preferences -> System -> General -> External scripting using: Local`
2. **Python 3.10 to 3.12**
   - DaVinci Resolve strictly requires Python 3.6 to 3.12 for its scripting API. 
   - Download from: [python.org/downloads](https://www.python.org/downloads/)
   - **Important:** During installation, make sure to check **"Add Python to PATH"**.
3. **Node.js (LTS version)**
   - Required to build and run the frontend UI.
   - Download from: [nodejs.org](https://nodejs.org/)

---

## 2. Installation Steps

### Step 1: Clone or Extract the Project
Extract the `Clip_Assassin_Resolve-v2.0.0` folder to your preferred location (e.g., Desktop or Documents).

### Step 2: Open Terminal / Command Prompt
Navigate to the project folder in your terminal:
- **Mac/Linux:** `cd /path/to/Clip_Assassin_Resolve-v2.0.0`
- **Windows:** `cd C:\path\to\Clip_Assassin_Resolve-v2.0.0`

### Step 3: Setup Python Virtual Environment
We highly recommend using a virtual environment to manage dependencies.

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install Python Dependencies
Install the required backend packages (FastAPI, Uvicorn, SQLite, etc.):
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is missing, you can run: `pip install fastapi uvicorn websockets pydantic`)*

### Step 5: Install Frontend Dependencies & Build UI
You need to install the Node packages for the React UI and build it once.

```bash
cd frontend
npm install
npm run build
cd ..
```
*(This creates the `frontend/dist` folder which the backend will serve).*

---

## 3. Running the Application (One-Click)

Once the setup is complete, you only need to use the one-click run script to start the app.

### Mac
Double-click the **`Run_Clip_Assassin.command`** file. 
- *Note: If it says "Permission denied", open Terminal and run `chmod +x Run_Clip_Assassin.command` first.*

### Windows
Double-click the **`RUN_CLIP_ASSASSIN.bat`** file.
*(You may need to create this file with the following contents if it doesn't exist):*
```cmd
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
start "Clip Assassin Backend" python server.py
timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000
```

### Linux
Run the following commands in the terminal:
```bash
source venv/bin/activate
python server.py
```
Then open your browser and go to `http://127.0.0.1:8000`

---

## 4. Troubleshooting

- **Error: No module named 'DaVinciResolveScript'**
  - **Mac:** Ensure your `PYTHONPATH` includes `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/`. The `.command` file does this automatically.
  - **Windows:** Ensure the system environment variable `PYTHONPATH` contains `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules\`.
  
- **Error: "External Scripting is disabled"**
  - Open DaVinci Resolve -> Preferences -> System -> General -> Set "External scripting using" to "Local" and restart Resolve.

- **UI not loading (404 Error on localhost:8000)**
  - Make sure you ran `npm run build` inside the `frontend` directory. The backend looks for the `frontend/dist` folder to serve the UI.
