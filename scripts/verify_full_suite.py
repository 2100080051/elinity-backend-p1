import requests
import sys
import json
import time

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
        print(f"✅ Login Success.")
        access_token = token_data.get('access_token')
        headers = {"Authorization": f"Bearer {access_token}"}
        
    except Exception as e:
        print(f"❌ Login Exception: {e}")
        return

    # 2. Endpoints List
    endpoints = [
        {"method": "GET",  "path": "/users/me", "desc": "User Profile"},
        {"method": "GET",  "path": "/chats/", "desc": "Chats"},
        {"method": "GET",  "path": "/journal/", "desc": "Get Journals"},
        {"method": "POST", "path": "/journal/", "json": {"title": "Test Journal", "content": "Testing upload endpoints."}, "desc": "Upload Journal", "expected": [200, 201]},
        {"method": "GET",  "path": "/groups/", "desc": "Groups"},
        {"method": "GET",  "path": "/members/", "desc": "Members"},
        {"method": "GET",  "path": "/onboarding/voice/start", "desc": "Onboarding (Voice)", "expected": [405]}, # Route Exists check
        {"method": "GET",  "path": "/room/", "desc": "Group Chat (Rooms)", "expected": [404]}, # Known Missing
        {"method": "GET",  "path": "/notifications/", "desc": "Notifications"},
        {"method": "GET",  "path": "/blogs/", "desc": "Blogs"},
        {"method": "GET",  "path": "/recommendations/", "desc": "Recommendations"},
        {"method": "GET",  "path": "/questions/cards/?count=1", "desc": "Question Cards"},
        {"method": "GET",  "path": "/events/", "desc": "Events"},
        {"method": "GET",  "path": "/feed/", "desc": "Social Feed"},
        {"method": "GET",  "path": "/tools/nudges", "desc": "Tools (Nudges)"},
        {"method": "GET",  "path": "/ai-mode/games/list", "desc": "AI Modes (Games)"},
        {"method": "GET",  "path": "/p1/connections/daily/romantic", "desc": "P1 Connections"},
        {"method": "GET",  "path": "/dashboard/me", "desc": "Dashboard (Skills/Evaluations Proxy)"},
        {"method": "GET",  "path": "/dashboard/relationship", "desc": "Relationship Dashboard"}
    ]

    print("\n🔍 Checking All Requested Endpoints...")
    results = []

    for ep in endpoints:
        url = f"{BASE_URL}{ep['path']}"
        method = ep['method']
        desc = ep['desc']
        
        # print(f"Checking {desc}...")
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=30)
            else:
                r = requests.post(url, headers=headers, json=ep.get("json"), timeout=30)
            
            status = r.status_code
            expected = ep.get("expected", [200, 201])
            
            passed = status in expected
            # 404 means Endpoint Missing (or object missing, but for lists it usually meant missing route)
            # 405 means Route Exists but wrong method (so endpoint exists)
            
            state = "✅" if passed else "❌"
            if status == 404: state = "⚠️ (Not Found)"
            elif status == 405: state = "✅ (Method Not Allowed - Exists)"
            
            results.append(f"| {desc:<25} | {method:<4} | {status} | {state:<15} |")
                 
        except Exception as e:
            results.append(f"| {desc:<25} | {method:<4} | ERR | ❌ {str(e)[:20]}... |")

    print("\n" + "="*70)
    print(f"| {'ENDPOINT':<25} | TECH | CODE | STATUS          |")
    print("-" * 70)
    for line in results:
        print(line)
    print("="*70)

if __name__ == "__main__":
    verify()
