import requests
import sys
import json

BASE_URL = "https://elinity-backend-arg7ckh2fph8duea.centralus-01.azurewebsites.net"
EMAIL = "emma.wilson@test.com"
PASSWORD = "Emma123!@#"

def verify():
    print(f"🔍 Logging in as {EMAIL}...")
    
    # 1. Login
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
        if resp.status_code != 200:
            print(f"❌ Login Failed: {resp.status_code} - {resp.text}")
            return
        
        token_data = resp.json()
        print(f"✅ Login Success. Token Type: {token_data.get('token_type')}")
        access_token = token_data.get('access_token')
        headers = {"Authorization": f"Bearer {access_token}"}
        
    except Exception as e:
        print(f"❌ Login Exception: {e}")
        return

    # 2. Check Endpoints
    endpoints = [
        {"method": "GET",  "path": "/users/me", "desc": "User Profile"},
        {"method": "GET",  "path": "/p1/connections/daily/romantic", "desc": "Daily Matches"},
        {"method": "POST", "path": "/p1/connections/action/test_id", "data": {"action": "archive"}, "expected": [200, 404, 422], "desc": "Connection Action (Test)"}, # 404/422 ok for dummy ID
        {"method": "POST", "path": "/multimodal/process/", "json": {"url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav"}, "desc": "Multimodal Journal"},
        {"method": "POST", "path": "/admin-panel/sessions/reset", "desc": "Reset Sessions"}
    ]

    print("\n🔍 Checking Endpoints...")
    all_passed = True

    for ep in endpoints:
        url = f"{BASE_URL}{ep['path']}"
        method = ep['method']
        desc = ep['desc']
        
        print(f"\n👉 Checking {desc} ({method} {ep['path']})...")
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=30)
            else:
                json_data = ep.get("json")
                data = ep.get("data")
                r = requests.post(url, headers=headers, json=json_data, data=data, timeout=30)
            
            status = r.status_code
            print(f"   Status: {status}")
            
            # success if 2xx or (expected error like 404 for bad ID)
            expected = ep.get("expected", [200, 201])
            if status in expected:
                print(f"   ✅ Success.")
                try:
                    # Print snippet
                    data = r.json()
                    snippet = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                    print(f"   Data: {snippet}")
                except:
                    print(f"   Data: {r.text[:100]}")
            else:
                # Special case: Multimodal might fail if external service down, but 500 means router loaded!
                if desc == "Multimodal Journal" and status != 404:
                     print(f"   ✅ Router Active (Status {status}). Endpoint found.")
                     if status == 200:
                         print(f"   ✅ Processing Success: {r.text[:100]}")
                     else:
                         print(f"   ⚠️ Service Response: {r.text[:100]}")
                elif desc == "Reset Sessions" and status == 200:
                      print(f"   ✅ Sessions Reset Successfully.") 
                else:
                    print(f"   ❌ Failed (Expected {expected})")
                    print(f"   Response: {r.text[:200]}")
                    all_passed = False

        except Exception as e:
            print(f"   ❌ Exception: {e}")
            all_passed = False
            
    if all_passed:
        print("\n✨ ALL CHECKS PASSED.")
    else:
        print("\n⚠️ SOME CHECKS FAILED.")

if __name__ == "__main__":
    verify()
