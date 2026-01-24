
import os
from dotenv import load_dotenv
import re

# Since we are running from scripts/, we need to load from ../.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Logic from settings.py essentially
_env_db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL")

if _env_db_url:
    print(f"✅ Found DB_URL/DATABASE_URL in env")
    
    # Check what kind of host it is (masking password)
    # Regex to capture: postgres://user:pass@HOST:PORT/db
    match = re.search(r"://.*:.*@([^:/]+)(:\d+)?/", _env_db_url)
    if match:
        host = match.group(1)
        print(f"🔍 Database Host: {host}")
        
        # Check pass
        db_user = _env_db_url.split("//")[1].split(":")[0]
        db_pass = _env_db_url.split(":")[2].split("@")[0]
        print(f"👤 DB User: {db_user}")
        print(f"🔑 Password length: {len(db_pass)}")
    else:
        print("⚠️ Could not parse hostname from URL (might be complex string)")
        print(f"First 15 chars: {_env_db_url[:15]}...")

else:
    print("❌ No direct DB_URL found. Checking fallback parts...")
    host = os.getenv('DB_HOST', 'Not Set')
    print(f"DB_HOST: {host}")

# Check Async Logic
print("\n--- Connection Test ---")
import socket
def check_dns(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS Resolved {hostname} -> {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS Failed for {hostname}: {e}")
        return False

if 'host' in locals():
    check_dns(host)
