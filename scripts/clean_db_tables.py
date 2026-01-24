
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "34.28.190.25")
DB_NAME = os.getenv("DB_NAME", "elinity")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Nani2906#")

print("Resetting database tables...")
try:
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Drop existing tables to clear type mismatch
    cur.execute("DROP TABLE IF EXISTS credit_purchases CASCADE;")
    cur.execute("DROP TABLE IF EXISTS transactions CASCADE;")
    cur.execute("DROP TABLE IF EXISTS api_usage_logs CASCADE;")
    cur.execute("DROP TABLE IF EXISTS subscriptions CASCADE;")  # Cause of issue (Integer vs String mismatch)
    cur.execute("DROP TABLE IF EXISTS plans CASCADE;")
    
    print("✅ Dropped problematic tables.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
