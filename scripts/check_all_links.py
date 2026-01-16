import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

def check_url(url):
    try:
        # Using powershell's Invoke-WebRequest for checking
        cmd = f'powershell -Command "Invoke-WebRequest -Uri {url} -Method Head -UseBasicParsing -ErrorAction SilentlyContinue | Select-Object -ExpandProperty StatusCode"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        status = result.stdout.strip()
        if status == "200":
            return url, "UP"
        else:
            # Try a GET request if HEAD fails or doesn't return 200 (some servers block HEAD)
            cmd = f'powershell -Command "Invoke-WebRequest -Uri {url} -Method Get -UseBasicParsing -ErrorAction SilentlyContinue | Select-Object -ExpandProperty StatusCode"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            status = result.stdout.strip()
            if status == "200":
                return url, "UP"
            return url, f"DOWN ({status if status else 'Timeout/Error'})"
    except Exception as e:
        return url, f"ERROR ({str(e)})"

def main():
    file_path = "c:/Users/nabhi/Downloads/python_elinity-main2/python_elinity-main/ELINITY_DEPLOYMENT_DIRECTORY.md"
    with open(file_path, 'r') as f:
        content = f.read()

    urls = re.findall(r'\[.*?\]\((https?://.*?)\)', content)
    unique_urls = list(set(urls))
    
    print(f"Found {len(unique_urls)} unique URLs. Checking status...")

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_url, unique_urls))

    print("\n--- Status Report ---")
    for url, status in sorted(results):
        print(f"{status.ljust(15)} | {url}")

if __name__ == "__main__":
    main()
