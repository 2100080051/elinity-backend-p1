import os
from pathlib import Path

WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"

def fix_configs():
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity")]
    print(f"Scanning {len(games)} games for config errors...")
    
    count = 0
    for game in games:
        config_path = GAMES_ROOT / game / "next.config.js"
        if config_path.exists():
            content = config_path.read_text(encoding='utf-8')
            if "output: \\'standalone\\'," in content:
                # Remove the bad line
                new_content = content.replace("  output: \\'standalone\\',", "").replace("output: \\'standalone\\',", "")
                # Clean up potential double newlines or empty lines if needed, but simple replace is safer
                config_path.write_text(new_content, encoding='utf-8')
                print(f"  Fixed {game}")
                count += 1
            elif "\\'standalone\\'" in content:
                 # Catch other formatting
                 print(f"  WARNING: {game} still has escaped quotes but pattern didn't match exactly.")
    
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    fix_configs()
