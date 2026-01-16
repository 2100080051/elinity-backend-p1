import os
import subprocess
import time

# CONFIGURATION
RG = "elinity-rg"
ACR_NAME = "elinityregistry123"
BACKEND_APP = "elinity-backend"
FRONTEND_APP = "elinity-the-story-weaver-docker" # Main premium app
FRONTEND_IMAGE_TAG = "elinity-premium-ui:latest"
BACKEND_IMAGE_TAG = "elinity-backend:latest"

# PATHS
WORKSPACE_ROOT = "c:/Users/nabhi/Downloads/python_elinity-main2/python_elinity-main"
GAME_UI_DIR = os.path.join(WORKSPACE_ROOT, "game-ui")

def run(cmd, cwd=None):
    print(f"Executing: {cmd}")
    try:
        # Force UTF-8 environment
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        res = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            encoding='utf-8', 
            errors='replace',
            env=env
        )
        if res.returncode != 0:
            print(f"FAILED: {res.stderr}")
            return False
        print(f"OK: {res.stdout.splitlines()[-1] if res.stdout else 'Done'}")
        return True
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

def main():
    print("🚀 STARTING V2 DEPLOYMENT (Unified Backend + Premium UI) 🚀")
    
    # 1. DEPLOY BACKEND
    print("\n--- 1. BUILDING BACKEND ---")
    # Build from root, assuming Dockerfile is there
    # Added --no-logs to prevent Windows encoding errors during output streaming
    cmd_backend_build = f"az acr build --registry {ACR_NAME} --image {BACKEND_IMAGE_TAG} --no-logs ."
    if not run(cmd_backend_build, cwd=WORKSPACE_ROOT):
        print("❌ Backend Build Failed. Aborting.")
        return

    print("\n--- 2. UPDATING BACKEND SERVICE ---")
    # Restart to pull new image
    # Force container update (Triggers pull)
    print("Force updating container config...")
    run(f"az webapp config container set --name {BACKEND_APP} --resource-group {RG} --docker-custom-image-name {ACR_NAME}.azurecr.io/{BACKEND_IMAGE_TAG}")
    
    # Restart
    run(f"az webapp restart --name {BACKEND_APP} --resource-group {RG}")
    
    # 2. DEPLOY FRONTEND (Unified UI)
    print("\n--- 3. BUILDING FRONTEND (UNIFIED UI) ---")
    # This image powers ALL premium games and now the Universal Lobby
    cmd_frontend_build = f"az acr build --registry {ACR_NAME} --image {FRONTEND_IMAGE_TAG} --build-arg VITE_API_URL=https://elinity-backend-arg7ckh2fph8duea.centralus-01.azurewebsites.net --no-logs ."
    if not run(cmd_frontend_build, cwd=GAME_UI_DIR):
        print("❌ Frontend Build Failed. Aborting.")
        return

    print("\n--- 4. UPDATING FRONTEND SERVICE ---")
    # Restart the main app to pull new image
    print("Force updating frontend container config...")
    run(f"az webapp config container set --name {FRONTEND_APP} --resource-group {RG} --docker-custom-image-name {ACR_NAME}.azurecr.io/{FRONTEND_IMAGE_TAG}")

    cmd_frontend_restart = f"az webapp restart --name {FRONTEND_APP} --resource-group {RG}"
    run(cmd_frontend_restart)

    print("\n✅ DEPLOYMENT COMPLETE!")
    print(f"Backend: https://{BACKEND_APP}.azurewebsites.net")
    print(f"Frontend: https://{FRONTEND_APP}.azurewebsites.net")
    print("Note: Other premium games will also update automatically within minutes since they share the image.")

if __name__ == "__main__":
    main()
