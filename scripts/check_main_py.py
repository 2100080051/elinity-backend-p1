import os
from pathlib import Path
import re

WORKSPACE_ROOT = Path("c:/Users/nabhi\Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"
MAIN_PY = WORKSPACE_ROOT / "python_elinity-main/main.py"

def check():
    if not MAIN_PY.exists():
        print("main.py not found")
        return

    content = MAIN_PY.read_text(encoding='utf-8')
    
    # Get all game folders
    game_folders = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity") and d != "elinity-ai-adventure-dungeon"]
    
    missing_mods = []
    missing_includes = []
    
    for game in game_folders:
        clean_name = game.replace("elinity-", "", 1).replace("-", "_")
        mod_name = f"games_{clean_name}"
        url_slug = clean_name.replace("_", "-")
        
        # Check _ROUTER_MODULES
        if f"'{mod_name}'" not in content and f'"{mod_name}"' not in content:
            missing_mods.append(mod_name)
            
        # Check _INCLUDES
        if f"'/games/{url_slug}'" not in content and f'"/games/{url_slug}"' not in content:
            missing_includes.append((f"/games/{url_slug}", mod_name))

    print(f"Missing Modules ({len(missing_mods)}):", missing_mods)
    print(f"Missing Includes ({len(missing_includes)}):", missing_includes)
    
    return missing_mods, missing_includes

if __name__ == "__main__":
    check()
