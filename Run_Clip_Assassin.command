#!/bin/bash
cd "$(dirname "$0")"

echo "Starting Clip Assassin..."

# Activate virtual environment
source venv/bin/activate

# Export DaVinci Resolve API paths
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

# Run the FastAPI server (it will automatically open the browser if sys.frozen is True, 
# but since we're running from source, we'll open it manually after a short delay)
(sleep 2 && open "http://127.0.0.1:8000") &

# Start Uvicorn server in production mode
python server.py
