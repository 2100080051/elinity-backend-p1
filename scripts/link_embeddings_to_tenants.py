#!/usr/bin/env python3
"""Link existing Milvus embedding ids to real tenants in Postgres.
This assigns embedding_id 1..N to the first N tenants found.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.session import Session
from models.user import Tenant

def run(n=5):
    db = Session()
    try:
        tenants = db.query(Tenant).limit(n).all()
        if not tenants:
            print('No tenants found to update')
            return
        for i, tenant in enumerate(tenants, start=1):
            tenant.embedding_id = i
            db.add(tenant)
            print(f"Set embedding_id={i} for tenant {tenant.id} (email={tenant.email})")
        db.commit()
        print('Done linking embeddings to tenants')
    except Exception as e:
        db.rollback()
        print('Error linking embeddings:', e)
    finally:
        db.close()

if __name__ == '__main__':
    run(5)
