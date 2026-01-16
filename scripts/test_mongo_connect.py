#!/usr/bin/env python3
"""
Test MongoDB connectivity using MONGO_DB_URL from the repository .env file.

Usage: run from the repo root. The script will parse `.env` for `MONGO_DB_URL`,
attempt to connect with `pymongo`, and print the outcome. Exit code 0 = success.
"""
import os
import sys
import re

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
mongo_url = os.environ.get('MONGO_DB_URL') or env.get('MONGO_DB_URL')
if not mongo_url:
    print('MONGO_DB_URL not found in environment or .env', file=sys.stderr)
    sys.exit(2)

try:
    # Import here so pip can be invoked before running if needed
    from pymongo import MongoClient
except Exception as e:
    print('pymongo not installed. Please run: pip install pymongo', file=sys.stderr)
    sys.exit(3)

print('Attempting to connect to MongoDB at', mongo_url)
try:
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    info = client.server_info()  # will throw if cannot connect
    print('Connected to MongoDB. Server info:')
    # print a subset
    print('  version:', info.get('version'))
    dbs = client.list_database_names()
    print('  databases (count):', len(dbs))
    print('  sample dbs:', dbs[:5])
    sys.exit(0)
except Exception as e:
    print('Failed to connect to MongoDB:', repr(e), file=sys.stderr)
    sys.exit(4)
