import os
from pathlib import Path

WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"

DOCKERIGNORE_CONTENT = """
.git
.next
node_modules
.env.local
.DS_Store
"""

def update_dockerignores():
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity")]
    print(f"Found {len(games)} games.")
    
    for game in games:
        ignore_path = GAMES_ROOT / game / ".dockerignore"
        # Always overwrite or append? Overwrite to be safe and ensure node_modules is there.
        ignore_path.write_text(DOCKERIGNORE_CONTENT, encoding='utf-8')
        print(f"Updated .dockerignore for {game}")

if __name__ == "__main__":
    update_dockerignores()
