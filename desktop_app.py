import os
import sys
import threading
import time
import uvicorn
import webview

# Import FastAPI app from server.py
from server import app

def start_backend_server():
    """Runs the FastAPI uvicorn server on localhost."""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def main():
    # 1. Start FastAPI server in a daemon background thread
    server_thread = threading.Thread(target=start_backend_server, daemon=True)
    server_thread.start()

    # Wait 1 second for the local server to start
    time.sleep(1.2)

    # 2. Create Native GUI Window via pywebview
    window = webview.create_window(
        title="Clip Assassin v2.0.1",
        url="http://127.0.0.1:8000",
        width=1280,
        height=850,
        min_size=(1024, 700),
        resizable=True,
        background_color="#0A0915",
        text_select=True
    )

    # 3. Start Native Webview Loop
    webview.start(private_mode=False)

if __name__ == "__main__":
    main()
