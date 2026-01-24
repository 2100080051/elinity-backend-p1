
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print(f"Connecting to {DB_HOST}...")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require' 
    )
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    print("\n✅ Connection Successful!")
    print(f"📊 Found {len(tables)} tables in database '{DB_NAME}':")
    for t in tables:
        print(f" - {t[0]}")
        
    if not tables:
        print("\n⚠️ The database is empty (no tables found).")
        print("This explains the 'relation \"tenants\" does not exist' error.")
        
    # Check alembic version
    try:
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        print(f"\n🏷️ Alembic Version in DB: {version[0] if version else 'None'}")
    except:
        print("\n🏷️ No 'alembic_version' table found.")

    conn.close()

except Exception as e:
    print(f"\n❌ Connection Failed: {e}")
