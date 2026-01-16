import os
import json
from pathlib import Path

WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"

REQUIRED_DEPS = {
    "framer-motion": "^10.0.0",
    "lucide-react": "^0.263.1",
    "axios": "^1.4.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^1.14.0"
}

def fix_dependencies():
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity")]
    print(f"Found {len(games)} games.")
    
    for game in games:
        pkg_path = GAMES_ROOT / game / "package.json"
        
        try:
            with open(pkg_path, 'r') as f:
                data = json.load(f)
            
            deps = data.get("dependencies", {})
            changed = False
            
            for dep, ver in REQUIRED_DEPS.items():
                if dep not in deps:
                    print(f"[{game}] Adding missing dependency: {dep}")
                    deps[dep] = ver
                    changed = True
            
            data["dependencies"] = deps
            
            if changed:
                with open(pkg_path, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"[{game}] Updated package.json")
                
        except Exception as e:
            print(f"[{game}] Error: {e}")

if __name__ == "__main__":
    fix_dependencies()
