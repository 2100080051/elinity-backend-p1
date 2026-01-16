import os
import re
from pathlib import Path

CORE_MODULES = [
    'auth', 'users', 'journal', 'social_feed', 'ai_modes', 'events', 'admin_panel',
    'chats', 'groups', 'members', 'question_cards', 'lumi', 'skill_evaluation',
    'billing', 'search', 'tools', 'recommendations',
    'notifications', 'upload_file', 'user_dashboard', 'blogs'
]

ROUTERS_DIR = Path("api/routers")

def update_main():
    # 1. Find valid game modules
    game_modules = []
    if ROUTERS_DIR.exists():
        for f in os.listdir(ROUTERS_DIR):
            if f.startswith("games_") and f.endswith(".py"):
                path = ROUTERS_DIR / f
                if path.stat().st_size > 2000:
                    game_modules.append(f[:-3])
    
    game_modules.sort()
    
    # 2. Combine lists
    full_list = CORE_MODULES + game_modules
    
    # 3. Format as Python list string
    list_str = "_ROUTER_MODULES = [\n"
    # Core
    for mod in CORE_MODULES:
        list_str += f"    '{mod}',\n"
    # Games (commented section)
    list_str += "    # Games\n"
    for mod in game_modules:
        list_str += f"    '{mod}',\n"
    list_str += "]"

    # 4. Read main.py
    main_path = Path("main.py")
    if not main_path.exists():
        print("main.py not found")
        return

    content = main_path.read_text(encoding="utf-8")
    
    # 5. Replace
    # Regex to find _ROUTER_MODULES = [ ... ]
    # We handle newlines via DOTALL
    new_content = re.sub(
        r"_ROUTER_MODULES\s*=\s*\[.*?\]", 
        list_str, 
        content, 
        flags=re.DOTALL
    )
    
    main_path.write_text(new_content, encoding="utf-8")
    print(f"Updated main.py with {len(game_modules)} game modules.")
    print("Core modules preserved.")

if __name__ == "__main__":
    update_main()
