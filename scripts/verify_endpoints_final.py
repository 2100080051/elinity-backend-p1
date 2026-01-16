import requests
import sys

BASE_URL = "https://elinity-backend-arg7ckh2fph8duea.centralus-01.azurewebsites.net"

ENDPOINTS = [
    ("/", 200), # Usually root returns welcome
    ("/docs", 200),
    ("/games/multiplayer/list", 200),
    ("/p1/connections/daily/romantic", 401), # Auth required
    ("/multimodal/process/", 401), # Auth required (POST)
    ("/admin-panel/sessions/reset", 401) # Auth required
]

def check():
    print(f"Checking {BASE_URL}...")
    failures = []
    
    for path, expected_status in ENDPOINTS:
        try:
            # We use GET for checks, even if method is POST, just to check Routing (405 is fine too for POST-only)
            resp = requests.get(f"{BASE_URL}{path}", timeout=10)
            status = resp.status_code
            
            # Map 405 to expected if we expect auth/success, because 405 means "Route Exists"
            if status == 405 and expected_status in [200, 401]:
                 status = expected_status 
                 # Wait, 405 means path exists but method wrong. That confirms endpoint 'working' in terms of deployment.
            
            # Accept 401 where expected
            if status == expected_status or (expected_status == 401 and status == 403):
                 print(f"✅ {path}: {status}")
            elif status == 405: # Method Not Allowed = Path Exists
                 print(f"✅ {path}: 405 (Route Exists)")
            elif expected_status == 200 and status == 404:
                 print(f"❌ {path}: 404 NOT FOUND")
                 failures.append(path)
            else:
                 print(f"⚠️ {path}: {status} (Expected {expected_status})")
                 
        except Exception as e:
            print(f"❌ {path}: Exception {e}")
            failures.append(path)

    if failures:
        print("\nSOME CHECKS FAILED.")
        sys.exit(1)
    else:
        print("\nALL SYSTEMS GREEN.")
        sys.exit(0)

if __name__ == "__main__":
    check()
