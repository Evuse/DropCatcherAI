import os
import sys
import shutil

def is_frozen():
    return getattr(sys, 'frozen', False)

def get_base_dir():
    if is_frozen():
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_runtime_dir():
    if is_frozen():
        app_support = os.path.expanduser("~/Library/Application Support/DropCatcher")
        os.makedirs(app_support, exist_ok=True)
        return app_support
    return get_base_dir()

def get_env_path():
    return os.path.join(get_runtime_dir(), ".env")

def get_db_path():
    return os.path.join(get_runtime_dir(), "dropcatcher.db")

def get_downloads_dir():
    downloads_dir = os.path.join(get_runtime_dir(), "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    return downloads_dir

def bootstrap_runtime():
    runtime_dir = get_runtime_dir()
    env_path = get_env_path()
    
    if is_frozen():
        template_path = os.path.join(get_base_dir(), ".env.example")
        if not os.path.exists(env_path) and os.path.exists(template_path):
            shutil.copy(template_path, env_path)
