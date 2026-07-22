import os
import sys
import shutil
import subprocess

def build_app():
    print("==================================================")
    print("🚀 Building Clip Assassin Native Desktop App...")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")

    # 1. Build React Frontend
    print("\n📦 Step 1: Building React Frontend Bundle...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    res = subprocess.run([npm_cmd, "run", "build"], cwd=frontend_dir)
    if res.returncode != 0:
        print("❌ Frontend build failed!")
        sys.exit(1)
    print("✓ Frontend bundle created successfully in frontend/dist")

    # 2. Select Platform Icon
    icon_arg = []
    if sys.platform == "darwin":
        icns_path = os.path.join(base_dir, "app_icon.icns")
        if os.path.exists(icns_path):
            icon_arg = ["--icon", icns_path]
    elif sys.platform == "win32":
        ico_path = os.path.join(base_dir, "icon.ico")
        if os.path.exists(ico_path):
            icon_arg = ["--icon", ico_path]

    # 3. Construct PyInstaller Command
    sep = ";" if sys.platform == "win32" else ":"
    
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name=Clip Assassin",
        f"--add-data=frontend/dist{sep}frontend/dist",
        f"--add-data=presets{sep}presets",
        f"--add-data=templates{sep}templates",
        "--collect-all=pywebview",
        "--collect-all=uvicorn",
        "--collect-all=fastapi",
    ] + icon_arg + ["desktop_app.py"]

    # 4. Run PyInstaller
    print("\n⚙️ Step 2: Compiling Native Desktop Binary with PyInstaller...")
    res = subprocess.run(pyinstaller_cmd, cwd=base_dir)
    if res.returncode != 0:
        print("❌ PyInstaller build failed!")
        sys.exit(1)

    print("\n==================================================")
    if sys.platform == "darwin":
        print("🎉 SUCCESS! Standalone macOS App created:")
        print(f"👉 {os.path.join(base_dir, 'dist', 'Clip Assassin.app')}")
    elif sys.platform == "win32":
        print("🎉 SUCCESS! Standalone Windows Executable created:")
        print(f"👉 {os.path.join(base_dir, 'dist', 'Clip Assassin.exe')}")
    print("==================================================")

if __name__ == "__main__":
    build_app()
