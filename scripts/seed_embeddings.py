#!/usr/bin/env python3
"""Seed a few sample profile embeddings into Milvus for testing.
Idempotent and safe: creates 5 synthetic profiles and upserts them.
"""
import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timezone
from elinity_ai.embeddings._embeddings import ElinityEmbedding
from elinity_ai.embeddings._milvus import milvus_client
import numpy as np

def make_sample_profile(i):
    return {
        "id": f"sample-{i}",
        "first_name": f"Sample{i}",
        "bio": f"I enjoy product engineering, startups, and open-source. I work on backend APIs and embeddings.",
        "interests": ["engineering", "startups", "ai"]
    }

def run():
    emb = ElinityEmbedding()
    items = []
    now = datetime.now(timezone.utc).isoformat()
    for i in range(1,6):
        profile = make_sample_profile(i)
        desc, vector = emb.create_embedding(profile)
        if desc is None or vector is None:
            print(f"Skipping profile {profile['id']} - failed to create embedding")
            continue
        if isinstance(vector, (np.ndarray,)):
            vector_list = vector.tolist()
        else:
            try:
                vector_list = list(vector)
            except Exception:
                vector_list = vector

        metadata = {
            "created_at": now,
            "source": "profile_embedding",
            "tenant": profile,
            "id": i,
            "vector": vector_list,
            "bio": desc,
        }
        items.append(metadata)

    if not items:
        print("No embeddings prepared, aborting.")
        return

    print(f"Upserting {len(items)} embeddings into Milvus (collection: {milvus_client.collection_name})...")
    try:
        res = milvus_client.upsert(items)
        print("Upsert result:", res)
    except Exception as e:
        print("Error upserting into Milvus:", e)

if __name__ == '__main__':
    run()
