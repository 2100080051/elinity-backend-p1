import os
from pathlib import Path

WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"
TEMPLATE_PATH = GAMES_ROOT / "elinity-ai-adventure-dungeon" / "Dockerfile"

def generate_dockerfiles():
    if not TEMPLATE_PATH.exists():
        print("Error: Pilot Dockerfile not found!")
        return

    template_content = TEMPLATE_PATH.read_text(encoding='utf-8')
    
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity")]
    print(f"Found {len(games)} games. Generating Dockerfiles...")
    
    for game in games:
        game_dir = GAMES_ROOT / game
        dockerfile_path = game_dir / "Dockerfile"
        
        # specific check: simple overwrite for now, assuming all key games are Next.js
        # (migrate_games.py already validated package.json structure)
        
        dockerfile_path.write_text(template_content, encoding='utf-8')
        print(f"  Created Dockerfile for {game}")

        # Also copy .dockerignore
        ignore_template = TEMPLATE_PATH.parent / ".dockerignore"
        if ignore_template.exists():
            ignore_content = ignore_template.read_text(encoding='utf-8')
            (game_dir / ".dockerignore").write_text(ignore_content, encoding='utf-8')

    print("Success! All games now have Dockerfiles.")

if __name__ == "__main__":
    generate_dockerfiles()
