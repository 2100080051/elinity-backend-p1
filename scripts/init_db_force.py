
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import engine, Base
# Import all models to ensure they are registered with Base.metadata
from models import (
    user, 
    game_session, 
    chat, 
    conversation, 
    journal, 
    question_card, 
    social, 
    activity,
    blogs,
    connection,
    credits,
    evaluation,
    lifebook,
    notifications,
    platform,
    service_key,
    tools
)

print(" forcing table creation via metadata.create_all...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
except Exception as e:
    print(f"❌ Failed to create tables: {e}")
