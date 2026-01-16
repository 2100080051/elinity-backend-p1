from fastapi import APIRouter, Depends, WebSocket
from fastapi.encoders import jsonable_encoder
import logging 
from schemas.chat import ChatSchema, GroupSchema
from utils.websockets import manager
from utils.token import get_current_user
from fastapi import HTTPException
from fastapi import status
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat import Chat, Group
from models.user import Tenant
from sqlalchemy.future import select
from elinity_ai.elinity_bot import ElinityChatbot
from typing import List 
import uuid
from datetime import datetime, timezone
from sqlalchemy import desc

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("group_chat")

router = APIRouter()

@router.post('/send-ai-message/{room_id}/', tags=["Group Chat"])
async def send_ai_message(room_id: str, conversation: List[dict], db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Group).where(Group.id == room_id))
    group = result.scalars().first()
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room ID.")
    try: 
        elinity_chatbot = ElinityChatbot(history=conversation)
        chat = Chat(group=room_id, message=elinity_chatbot.get_message())
        db.add(chat)
        await db.commit()
    
        await manager.broadcast(room_id, jsonable_encoder(chat))
        return chat
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.websocket('/ws/{room_id}')
async def group_chat(websocket: WebSocket, room_id: str, db: AsyncSession = Depends(get_async_db)):
    # RESOLVE ROOM ID: It could be a session_id or a Group UUID
    result = await db.execute(select(Group).where((Group.id == room_id) | (Group.name == f"game_{room_id}")))
    group = result.scalars().first()
    
    actual_room_id = group.id if group else room_id

    await manager.connect(websocket, room_id)
    
    try:
        # 1. Try Authentication via Query Parameter
        user_id = websocket.query_params.get("userId")
        current_user_id = None
        
        if user_id:
             # Check if guest exists
             result = await db.execute(select(Tenant).where(Tenant.id == user_id))
             current_user = result.scalars().first()
             
             # AUTO-CREATE GUEST if missing
             if not current_user:
                 try:
                     new_guest = Tenant(
                         id=user_id,
                         email=f"guest_{user_id}@elinity.ai", 
                         password="guest_password",
                         role="user"
                     )
                     db.add(new_guest)
                     await db.commit()
                     current_user_id = user_id
                     print(f"WS Created Guest User: {user_id}")
                 except Exception as exc:
                     print(f"Failed to auto-create guest in WS: {exc}")
                     await db.rollback()
             else:
                 current_user_id = current_user.id

        if not current_user_id:
            print(f"WS Auth Failed for room {room_id}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # LOAD HISTORY from DB (use actual_room_id for persistence)
        try:
            history_query = select(Chat).where(Chat.group == actual_room_id).order_by(desc(Chat.created_at)).limit(50)
            history_result = await db.execute(history_query)
            messages = history_result.scalars().all()
            for msg in reversed(messages):
                await websocket.send_json({
                    "id": str(msg.id),
                    "sender": msg.sender,
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "type": "chat"
                })
        except Exception as e:
            print(f"Error loading chat history: {e}")

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "chat")
            
            chat_data = {
                "id": str(uuid.uuid4()),
                "sender": current_user_id,
                "message": data.get("message"),
                "group": room_id, # Frontend expects connection room_id
                "created_at": datetime.now(timezone.utc).isoformat(),
                "type": msg_type
            }

            # SAVE TO DB if it's a chat message (use actual_room_id)
            if msg_type == "chat" and data.get("message") and actual_room_id:
                try:
                    new_chat = Chat(
                        id=chat_data["id"],
                        sender=current_user_id,
                        group=actual_room_id,
                        message=data.get("message")
                    )
                    db.add(new_chat)
                    await db.commit()
                except Exception as db_err:
                    print(f"Failed to save chat to DB: {db_err}")
                    await db.rollback()
            
            await manager.broadcast(room_id, jsonable_encoder(chat_data)) 

    except Exception as e:
        print(f"WS Disconnect: {e}")
        await manager.disconnect(websocket, room_id)
