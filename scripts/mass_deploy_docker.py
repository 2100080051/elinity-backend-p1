import os
import subprocess
import json
import concurrent.futures
from pathlib import Path

# CONFIGURATION
RG = "elinity-rg"
ACR_NAME = "elinityregistry123"
PLAN = "elinity-docker-plan"
BACKEND_URL = "https://elinity-backend-arg7ckh2fph8duea.centralus-01.azurewebsites.net"
ACR_SERVER = f"{ACR_NAME}.azurecr.io"
# Need to fetch these dynamically or hardcode if known from previous step (step 918)
ACR_USER = "elinityregistry123"
ACR_PASS = os.getenv("ACR_PASS")

WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"
LOG_FILE = WORKSPACE_ROOT / "deployment_results.md"

def run_cmd(cmd, cwd=None):
    """Runs a shell command and returns output."""
    try:
        # Force UTF-8 for Azure CLI output on Windows
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # shell=True for Windows
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            encoding='utf-8', 
            errors='replace', 
            env=env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def deploy_game(game_name):
    """Orchestrates deployment for a single game."""
    game_dir = GAMES_ROOT / game_name
    image_tag = f"{game_name}:latest"
    full_image = f"{ACR_SERVER}/{image_tag}"
    app_name = f"{game_name}-docker"

    print(f"[{game_name}] Starting Deployment...")

    # print(f"[{game_name}] 0. Checking status...")
    # check_cmd = f"az webapp show --name {app_name} --resource-group {RG} --query defaultHostName -o tsv"
    # ok, out, err = run_cmd(check_cmd)
    # if ok and out.strip():
    #     url = f"https://{out.strip()}"
    #     print(f"[{game_name}] App exists at {url}. Will update.")

    # 1. ACR Build
    print(f"[{game_name}] 1. Building Image on Azure Cloud...")
    # --no-wait doesn't allow us to know when it's done for the next step (Create needs image?)
    # Actually 'webapp create' can be run even if image logic is pulling, but it might fail to start initially.
    # Let's run synchronous build for safety, or we can assume it takes 2 mins.
    # To save time, we will run build synchronously here (in thread).
    
    # Adding --no-logs to prevent Windows UnicodeEncodeError on progress bars
    build_cmd = f"az acr build --registry {ACR_NAME} --image {image_tag} --build-arg NEXT_PUBLIC_P1_BACKEND_URL={BACKEND_URL} --no-logs ."
    ok, out, err = run_cmd(build_cmd, cwd=game_dir)
    if not ok:
        print(f"[{game_name}] BUILD FAILED: {err}")
        return False, f"Build Failed"

    # 2. Create Web App
    print(f"[{game_name}] 2. Creating Web App {app_name}...")
    create_cmd = f"az webapp create --resource-group {RG} --plan {PLAN} --name {app_name} --deployment-container-image-name {full_image}"
    ok, out, err = run_cmd(create_cmd)
    
    # 3. Configure Auth (If create failed, it might verify image existence)
    if not ok and "Conflict" not in err: # If conflict, app exists, proceed to update
         print(f"[{game_name}] CREATE FAILED: {err}")
         return False, f"Create Failed: {err}"

    # 4. Config Container Auth
    print(f"[{game_name}] 3. Configuring Credentials...")
    auth_cmd = (
        f"az webapp config container set --name {app_name} --resource-group {RG} "
        f"--docker-custom-image-name {full_image} "
        f"--docker-registry-server-url https://{ACR_SERVER} "
        f"--docker-registry-server-user {ACR_USER} "
        f"--docker-registry-server-password \"{ACR_PASS}\""
    )
    ok, out, err = run_cmd(auth_cmd)
    if not ok:
        print(f"[{game_name}] AUTH CONFIG FAILED: {err}")
        return False, "Auth Failed"
    
    # 5. Get URL
    print(f"[{game_name}] 4. Retrieving URL...")
    url_cmd = f"az webapp show --name {app_name} --resource-group {RG} --query defaultHostName -o tsv"
    ok, out, err = run_cmd(url_cmd)
    url = f"https://{out.strip()}"
    
    print(f"[{game_name}] SUCCESS! URL: {url}")
    return True, url

def main():
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity") and d != "elinity-ai-adventure-dungeon"]
    print(f"Found {len(games)} games to deploy.")

    # Limit to 2 for test run, or all?
    # User said "implement them".
    # Enabling ALL deployment by default now that verification is complete.
    target_games = games 
    # target_games = ["elinity-ai-comic-creator"]  # Test mode
    
    results = {}
    
    # Using ThreadPool to parallelize if multiple
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_game = {executor.submit(deploy_game, game): game for game in target_games}
        for future in concurrent.futures.as_completed(future_to_game):
            game = future_to_game[future]
            try:
                success, data = future.result()
                results[game] = data
            except Exception as exc:
                print(f"{game} generated an exception: {exc}")

    # Write results
    with open(LOG_FILE, "a") as f:
        for game, result in results.items():
            f.write(f"- **{game}**: {result}\n")
            
if __name__ == "__main__":
    main()
