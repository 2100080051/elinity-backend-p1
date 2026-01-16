import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

def check_url(url):
    # Retry logic for Azure cold starts
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Increase timeout to 60 seconds for Azure
            cmd = f'powershell -Command "Invoke-WebRequest -Uri {url} -Method Get -UseBasicParsing -TimeoutSec 60 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty StatusCode"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            status = result.stdout.strip()
            if status == "200":
                return url, "UP"
            
            # If we get a 503 or 502, Azure might be starting up, so wait and retry
            if status in ["502", "503", ""]:
                time.sleep(10 * (attempt + 1))
                continue
                
            return url, f"DOWN ({status if status else 'Timeout/Error'})"
        except Exception as e:
            if attempt == max_retries - 1:
                return url, f"ERROR ({str(e)})"
            time.sleep(5)
    return url, "DOWN (Cold Start Failure)"

def main():
    file_path = "c:/Users/nabhi/Downloads/python_elinity-main2/python_elinity-main/ELINITY_DEPLOYMENT_DIRECTORY.md"
    with open(file_path, 'r') as f:
        content = f.read()

    urls = re.findall(r'\[.*?\]\((https?://.*?)\)', content)
    unique_urls = list(set(urls))
    
    print(f"Found {len(unique_urls)} unique URLs. Checking status (this may take 2-3 minutes due to Azure cold starts)...")

    results = []
    # Using fewer workers to avoid overwhelming the local machine/shell
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_url, unique_urls))

    # Generate Markdown Report
    report = "# Elinity Link Status Report\n\n"
    report += f"**Checked at:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += "| Status | URL |\n"
    report += "| :--- | :--- |\n"
    
    for url, status in sorted(results):
        icon = "✅" if status == "UP" else "❌"
        report += f"| {icon} {status} | {url} |\n"

    report_path = "c:/Users/nabhi/Downloads/python_elinity-main2/python_elinity-main/LINK_CHECK_RESULTS.md"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nReport generated: {report_path}")

if __name__ == "__main__":
    main()
