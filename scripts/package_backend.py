import shutil
import os
import zipfile
from pathlib import Path

# Config
WORKSPACE = Path("c:/Users/nabhi/Downloads/python_elinity-main2/python_elinity-main")
OUTPUT_ZIP = WORKSPACE.parent / "backend_deploy.zip"

EXCLUDES = {
    "__pycache__", 
    ".git", 
    ".vscode", 
    "venv", 
    "env", 
    "node_modules", 
    ".idea", 
    "tests", 
    "azure_deployments"
}

def package_backend():
    print(f"Packaging Backend from {WORKSPACE}...")
    
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()
        
    count = 0
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(WORKSPACE):
            # Filtering
            dirs[:] = [d for d in dirs if d not in EXCLUDES]
            
            for file in files:
                if file.endswith(".zip") or file.endswith(".log") or file in [".env", ".DS_Store"]:
                    continue
                    
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(WORKSPACE)
                
                # Check for hidden files/folders in path
                if any(part.startswith('.') for part in rel_path.parts if part != '.'):
                     continue

                zipf.write(abs_path, rel_path)
                count += 1
                
    print(f"Success! Created {OUTPUT_ZIP} ({count} files)")

if __name__ == "__main__":
    package_backend()
