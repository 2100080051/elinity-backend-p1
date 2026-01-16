import os
import shutil

# Files to remove
FILES_TO_REMOVE = [
    "debug_ready_400.py",
    "test_live_chat_v2.py",
    "test_live_chat_v3.py",
    "update_complete_profiles.py",
    "check_results.txt",
    "all_deployments.json",
    "apps.json",
    "webapps.json",
    "scripts/cleanup_sessions.py"
]

# Patterns or dirs
DIRS_TO_REMOVE = [
    "logs_temp",
    "__pycache__"
]

def clean():
    root = os.getcwd()
    print(f"Cleaning in {root}...")
    
    # Files
    for f in FILES_TO_REMOVE:
        path = os.path.join(root, f)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Deleted: {f}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")
                
    # Dirs
    for d in DIRS_TO_REMOVE:
        path = os.path.join(root, d)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"Deleted Dir: {d}")
            except Exception as e:
                print(f"Failed to delete dir {d}: {e}")
                
    # Recursive pycache
    for root_dir, dirs, files in os.walk(root):
        if "__pycache__" in dirs:
            try:
                shutil.rmtree(os.path.join(root_dir, "__pycache__"))
                print(f"Deleted cache: {os.path.join(root_dir, '__pycache__')}")
            except: pass

if __name__ == "__main__":
    clean()
