import os
import sys
import threading
import time
import webview
import uvicorn
from app.paths import bootstrap_runtime

def start_server():
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def main():
    # Bootstrap runtime environment (Application Support)
    bootstrap_runtime()
    
    # Start FastAPI server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Create pywebview window
    webview.create_window(
        "DropCatcher", 
        "http://127.0.0.1:8000/",
        width=1200, 
        height=800,
        min_size=(800, 600)
    )
    webview.start()

if __name__ == "__main__":
    main()
