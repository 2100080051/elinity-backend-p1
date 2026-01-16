import os
import shutil
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"
DEPLOY_DIR = GAMES_ROOT / "azure_deployments"

EXCLUSIONS = ['node_modules', '.next', '.git', '.vscode', 'azure_deployments', '__pycache__']

def package_games():
    if not DEPLOY_DIR.exists():
        DEPLOY_DIR.mkdir()

    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir()]

    print(f"Found {len(games)} directories.")

    count = 0
    for game in games:
        game_path = GAMES_ROOT / game
        
        # Skip non-games
        if game.startswith(".") or game == "azure_deployments" or game == "node_modules":
            continue
        
        # Determine if it's a game (has package.json)
        if not (game_path / "package.json").exists():
            continue

        print(f"Packaging {game}...")
        
        # Create ZIP
        # shutil.make_archive base_name is the file to create (without ext), root_dir is where to zip from
        zip_base = DEPLOY_DIR / game
        
        try:
            # We use a custom filter logic if using Python 3.8+, but easier is to Copy to Temp then Zip
            # To avoid copying massive node_modules, we must implement exclusion.
            # shutil.make_archive doesn't support exclusion easily.
            # So we use zipfile module directly.
            
            import zipfile
            
            zip_filename = f"{zip_base}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(game_path):
                    # Filter dirs in-place to skip traversal
                    dirs[:] = [d for d in dirs if d not in EXCLUSIONS]
                    
                    for file in files:
                        if file in EXCLUSIONS: continue
                        
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, game_path)
                        zf.write(abs_path, rel_path)
                        
            print(f"  Created {zip_filename}")
            count += 1
            
        except Exception as e:
            print(f"  Failed to zip {game}: {e}")

    print(f"Packaging Complete. {count} Zips created inside {DEPLOY_DIR}")

if __name__ == "__main__":
    package_games()
