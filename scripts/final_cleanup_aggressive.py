import os
import glob
import shutil

def aggressive_clean():
    root = os.getcwd()
    print(f"Aggressive cleaning in {root}...")

    # Patterns to match and DELETE
    patterns = [
        "FOUNDER_*.md",
        "P2_*.md",
        "DEPLOYMENT_*.md",
        "ELINITY_*.md",
        "README_*.md",
        "*.ps1",
        "API_INTEGRATION_GUIDE.md",
        "TEST_ACCOUNTS_READY.md",
        "final_deployment_*.md",
        "final_deployment_*.txt",
        "*.docx",
        "check_results.txt",
        "all_deployments.json",
        "apps.json",
        "webapps.json"
    ]

    for pattern in patterns:
        files = glob.glob(os.path.join(root, pattern))
        for f in files:
            try:
                os.remove(f)
                print(f"Deleted: {os.path.basename(f)}")
            except Exception as e:
                print(f"Error deleting {os.path.basename(f)}: {e}")

    # Remove specific old scripts if present
    extra_files = ["quick_fix.ps1", "redeploy_backend.ps1", "retry_failed_games.ps1"]
    for f in extra_files:
        path = os.path.join(root, f)
        if os.path.exists(path):
             try:
                os.remove(path)
                print(f"Deleted: {f}")
             except: pass

if __name__ == "__main__":
    aggressive_clean()
