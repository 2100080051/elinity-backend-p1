"""Diagnostic script to test Postgres connectivity and SSL modes.

Run this on the deployment VM to reproduce the psycopg2/SSL error and gather
provider-specific details (useful for Render/Postgres or other managed DBs).

Usage:
  python scripts/check_db_connection.py

It reads DB_* vars from the environment or from a `.env` file in the project root.
"""
import os
import socket
import traceback
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

try:
    host_ip = socket.gethostbyname(DB_HOST) if DB_HOST else None
except Exception:
    host_ip = None

print("Postgres diagnostic")
print("- DB_HOST:", DB_HOST)
print("- Resolved IP:", host_ip)
print("- DB_PORT:", DB_PORT)
print("- DB_NAME:", DB_NAME)
print("- DB_USER:", DB_USER)
print("")

sslmodes = ["require", "verify-ca", "verify-full", "prefer", "allow", "disable"]

try:
    import psycopg2
    from psycopg2 import OperationalError
except Exception as e:
    print("psycopg2 is not installed in this environment:", e)
    print("Install with: python -m pip install psycopg2-binary")
    raise SystemExit(1)

for mode in sslmodes:
    dsn = (
        f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} sslmode={mode}"
    )
    print(f"Trying sslmode={mode} ...")
    try:
        conn = psycopg2.connect(dsn, connect_timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        ver = cur.fetchone()
        print("  Connected ok. Postgres version:", ver)
        cur.close()
        conn.close()
    except OperationalError as oe:
        print("  OperationalError:")
        traceback.print_exception(type(oe), oe, oe.__traceback__)
    except Exception as e:
        print("  Error:")
        traceback.print_exception(type(e), e, e.__traceback__)
    print("")

print("Diagnostic complete. If you see 'SSL connection has been closed unexpectedly',")
print("add the VM public IP to the DB provider allowlist (Render) or run migrations from a host already allowlisted.")
