import requests
import re
import concurrent.futures

DEPLOYMENT_FILE = "c:/Users/nabhi/Downloads/python_elinity-main2/deployment_results.md"

def get_urls():
    urls = {}
    with open(DEPLOYMENT_FILE, "r") as f:
        for line in f:
            match = re.search(r"- \*\*(.+?)\*\*: (https://.+)", line)
            if match:
                name = match.group(1)
                url = match.group(2)
                urls[name] = url # Overwrites duplicates with latest
    return urls

def check_url(name, url):
    try:
        resp = requests.get(url, timeout=10)
        return name, url, resp.status_code
    except Exception as e:
        return name, url, str(e)

def main():
    urls = get_urls()
    print(f"Checking {len(urls)} deployments...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_url, name, url): name for name, url in urls.items()}
        for future in concurrent.futures.as_completed(future_to_url):
            name, url, status = future.result()
            print(f"[{status}] {name}")
            results.append((name, status))
            
    print("\nSummary:")
    failed = [r for r in results if r[1] != 200]
    if not failed:
        print("ALL SYSTEMS GO! All deployments verify with 200 OK.")
    else:
        print(f"{len(failed)} deployments failed health check:")
        for name, status in failed:
            print(f" - {name}: {status}")

if __name__ == "__main__":
    main()
