#!/usr/bin/env python3
"""
Create a service key and store its hash in MongoDB (collection `service_keys`).

Behavior:
- Reads `MONGO_DB_URL` from the environment (or `.env` if present).
- Generates a secure random key, hashes it with the repo's pwd_context,
  inserts a document into `service_keys`, and prints the plain key once to stdout.
- Does NOT save the plain key to disk by default.

Run from the repo root: `python scripts/create_service_key_mongo.py`
"""
import os
import sys
import re
import secrets
from datetime import datetime

def load_env(path='.env'):
    if not os.path.exists(path):
        return {}
    env = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r"([^=]+)=(.*)", line)
            if not m:
                continue
            k = m.group(1).strip()
            v = m.group(2).strip().strip('"')
            env[k] = v
    return env

env = load_env('.env')
MONGO_DB_URL = os.environ.get('MONGO_DB_URL') or env.get('MONGO_DB_URL')
if not MONGO_DB_URL:
    print('MONGO_DB_URL not set in environment or .env', file=sys.stderr)
    sys.exit(2)

try:
    from pymongo import MongoClient
except Exception:
    print('Please install pymongo: pip install pymongo', file=sys.stderr)
    sys.exit(3)

try:
    # import pwd_context from the app utilities
    from utils.token import pwd_context
except Exception:
    print('Unable to import pwd_context from utils.token. Ensure you run from repo root with project on PYTHONPATH.', file=sys.stderr)
    sys.exit(4)

plain = secrets.token_urlsafe(48)
hashed = pwd_context.hash(plain)

try:
    client = MongoClient(MONGO_DB_URL, serverSelectionTimeoutMS=5000)
    db = client.get_default_database()
    coll = db.get_collection('service_keys')
    doc = {
        'key_hash': hashed,
        'created_at': datetime.utcnow(),
        'created_by': 'system',
        'note': 'P1→P2 integration key',
    }
    res = coll.insert_one(doc)
    print(plain)
    print('# NOTE: The plain key was printed above exactly once. Move it into a secret manager and do NOT keep it in source control.')
    sys.exit(0)
except Exception as e:
    print('Failed to insert service key into MongoDB:', repr(e), file=sys.stderr)
    sys.exit(5)
