import os
import subprocess
import sys
import platform

def build_app():
    print("Building Clip Assassin Desktop App...")
    
    # 1. Build React Frontend
    print("Step 1: Building React Frontend...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        print("Frontend built successfully.")
    except Exception as e:
        print(f"Error building frontend: {e}")
        return

    # 2. Package with PyInstaller
    print("Step 2: Packaging Python Backend...")
    
    # Determine separator for add-data based on OS
    sep = ";" if platform.system() == "Windows" else ":"
    
    frontend_dist = os.path.join("frontend", "dist")
    templates_dir = "templates"
    
    # Ensure templates directory exists
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        
    icon_file = "icon.ico" if platform.system() == "Windows" else "app_icon.icns"
        
    cmd = [
        "pyinstaller",
        "--name=ClipAssassin",
        "--noconfirm",
        "--onefile",
        f"--icon={icon_file}",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=uvicorn.lifespan.off",
        # "--windowed", # Uncomment to hide console window (can cause issues with FastAPI on some systems)
        f"--add-data={frontend_dist}{sep}{frontend_dist}",
        f"--add-data={templates_dir}{sep}{templates_dir}",
        "server.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\nSuccess! The standalone application has been created in the 'dist' folder.")
    except Exception as e:
        print(f"Error packaging app: {e}")

if __name__ == "__main__":
    build_app()
