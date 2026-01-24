
import asyncio
import json
import uuid
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import async_session
from models.user import User
from models.game_session import GameSession
from utils.token import get_password_hash
from utils.game_chat import create_game_chat_group, add_player_to_game_chat
from sqlalchemy.future import select

async def test_chat_setup():
    async with async_session() as db:
        print("Creating test users...")
        
        # 1. Create Host
        host_email = f"host_{uuid.uuid4()}@test.com"
        host = User(
            id=str(uuid.uuid4()),
            email=host_email,
            password=get_password_hash("password")
        )
        db.add(host)
        
        # 2. Create Player
        player_email = f"player_{uuid.uuid4()}@test.com"
        player = User(
            id=str(uuid.uuid4()),
            email=player_email,
            password=get_password_hash("password")
        )
        db.add(player)
        await db.commit()
        
        print(f"Users created:\nHost: {host.id}\nPlayer: {player.id}")
        
        # 3. Create Game Session
        session_id = str(uuid.uuid4())
        game_session = GameSession(
            session_id=session_id,
            game_slug="test-game",
            host_user_id=host.id,
            state={"status": "lobby"},
            players={host.id: {"role": "host"}}
        )
        db.add(game_session)
        await db.commit()
        print(f"Game session created: {session_id}")
        
        # 4. Create Chat Group for Game
        print("Creating chat group...")
        group_id = await create_game_chat_group(db, session_id, host.id)
        print(f"Chat Group Created: {group_id}")
        
        # 5. Add Player to Game & Chat
        print("Adding player to chat...")
        await add_player_to_game_chat(db, group_id, player.id)
        print("Player added to chat.")
        
        print("\n✅ Chat Setup Test Complete!")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_chat_setup())
