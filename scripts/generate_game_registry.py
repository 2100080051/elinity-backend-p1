import os
import json
import re
from pathlib import Path

WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"
OUTPUT_FILE = WORKSPACE_ROOT / "python_elinity-main/data/game_registry.json"

def generate_registry():
    print("Scanning games...")
    registry = []
    
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity")]
    
    for game_folder in games:
        # Slug
        if game_folder.startswith("elinity-"):
            clean_name = game_folder.replace("elinity-", "", 1).replace("-", "_")
            url_slug = clean_name.replace("_", "-")
        else:
            url_slug = game_folder
            
        game_data = {
            "id": url_slug,
            "title": game_folder.replace("elinity-", "").replace("-", " ").title(),
            "description": "An interactive AI experience.",
            "url": f"/games/{url_slug}", 
            "tags": ["AI", "Storytelling"]
        }
        
        # Extract from index.js
        frontend_index = GAMES_ROOT / game_folder / "pages" / "index.js"
        if frontend_index.exists():
            content = frontend_index.read_text(encoding='utf-8')
            
            title_match = re.search(r'const GAME_TITLE = "(.*?)";', content)
            if title_match: 
                game_data["title"] = title_match.group(1)
                
            # Infer tags/vibe from BG Prompt
            bg_match = re.search(r'const BG_PROMPT = "(.*?)";', content)
            if bg_match:
                prompt = bg_match.group(1).lower()
                if "cyber" in prompt: game_data["tags"].append("Sci-Fi")
                if "fantasy" in prompt: game_data["tags"].append("Fantasy")
                if "mystery" in prompt: game_data["tags"].append("Mystery")
                if "horror" in prompt: game_data["tags"].append("Horror")
                game_data["bg_prompt"] = bg_match.group(1)

        # Extract description from system prompt if available
        # Try multiple locations as per _system_prompt.py logic
        candidates = [
            GAMES_ROOT / game_folder / 'public' / 'system_prompt.txt',
            GAMES_ROOT / 'elinity game suite' / game_folder / 'public' / 'system_prompt.txt' # nested case
        ]
        
        for p in candidates:
            if p.exists():
                try:
                    text = p.read_text(encoding='utf-8')
                    # Take first sentence or first 100 chars
                    first_line = text.split('\n')[0]
                    if len(first_line) > 10:
                        game_data["description"] = first_line[:150] + ("..." if len(first_line)>150 else "")
                    break
                except: pass
        
        registry.append(game_data)

    # Ensure output dir exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    OUTPUT_FILE.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    print(f"Registry generated with {len(registry)} games at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_registry()
