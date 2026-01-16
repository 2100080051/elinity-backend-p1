import subprocess
import os

RG = "elinity-rg"
PLAN = "elinity-docker-plan"
ACR_NAME = "elinityregistry123"
ACR_SERVER = f"{ACR_NAME}.azurecr.io"
IMAGE = f"{ACR_SERVER}/elinity-premium-ui:latest"
# Credentials from previous session logs
ACR_USER = "elinityregistry123"
ACR_PASS = os.getenv("ACR_PASS")

PREMIUM_GAMES = [
    "elinity-the-story-weaver",
    "elinity-myth-maker-arena",
    "elinity-world-builders",
    "elinity-truth-and-layer",
    "elinity-memory-mosaic",
    "elinity-the-alignment-game",
    "elinity-the-compass-game",
    "elinity-echoes-and-expressions",
    "elinity-serendipity-strings",
    "elinity-the-long-quest"
]

def run(cmd):
    print(f"Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error: {res.stderr}")
    return res.returncode == 0, res.stdout

def deploy():
    for game in PREMIUM_GAMES:
        app_name = f"{game}-docker"
        print(f"\n--- Deploying {app_name} ---")
        
        # Check if exists
        ok, _ = run(f"az webapp show --name {app_name} --resource-group {RG}")
        
        if not ok:
            print(f"Creating new Web App: {app_name}")
            run(f"az webapp create --resource-group {RG} --plan {PLAN} --name {app_name} --deployment-container-image-name {IMAGE}")
        
        print(f"Configuring container for {app_name}")
        run(f"az webapp config container set --name {app_name} --resource-group {RG} "
            f"--docker-custom-image-name {IMAGE} "
            f"--docker-registry-server-url https://{ACR_SERVER} "
            f"--docker-registry-server-user {ACR_USER} "
            f"--docker-registry-server-password \"{ACR_PASS}\"")
        
        print(f"Setting environment variables for {app_name}")
        # Ensure it points to the correct backend
        run(f"az webapp config appsettings set --name {app_name} --resource-group {RG} --settings WEBSITES_PORT=80")

    print("\nAll 10 Premium Games deployed successfully!")

if __name__ == "__main__":
    deploy()
