import os
import subprocess
import time

# CONFIGURATION
RG = "elinity-rg"
ACR_NAME = "elinityregistry123"
FRONTEND_APP = "elinity-the-story-weaver-docker" 
FRONTEND_IMAGE_TAG = "elinity-premium-ui:latest"

# PATHS
WORKSPACE_ROOT = "c:/Users/nabhi/Downloads/python_elinity-main2/python_elinity-main"
GAME_UI_DIR = os.path.join(WORKSPACE_ROOT, "game-ui")

def run(cmd, cwd=None):
    print(f"Executing: {cmd}")
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', env=env)
        if res.returncode != 0:
            print(f"FAILED: {res.stderr}")
            if "ContainerConfigSet" in str(res.stderr):
                 pass # Ignore benign Azure CLI noise
            else:
                 return False
        print(f"OK: {res.stdout.splitlines()[-1] if res.stdout else 'Done'}")
        return True
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

def main():
    print("🚀 STARTING FRONTEND-ONLY DEPLOYMENT (Fast Track) 🚀")
    
    # 2. DEPLOY FRONTEND
    print("\n--- BUILDING FRONTEND ---")
    cmd_frontend_build = f"az acr build --registry {ACR_NAME} --image {FRONTEND_IMAGE_TAG} --build-arg VITE_API_URL=https://elinity-backend-arg7ckh2fph8duea.centralus-01.azurewebsites.net --no-logs ."
    if not run(cmd_frontend_build, cwd=GAME_UI_DIR):
        print("❌ Frontend Build Failed.")
        return

    print("\n--- UPDATING FRONTEND SERVICE ---")
    print("Force updating frontend container config...")
    run(f"az webapp config container set --name {FRONTEND_APP} --resource-group {RG} --docker-custom-image-name {ACR_NAME}.azurecr.io/{FRONTEND_IMAGE_TAG}")

    cmd_frontend_restart = f"az webapp restart --name {FRONTEND_APP} --resource-group {RG}"
    run(cmd_frontend_restart)

    print("\n✅ DEPLOYMENT COMPLETE!")
    print(f"Frontend: https://{FRONTEND_APP}.azurewebsites.net")

if __name__ == "__main__":
    main()
