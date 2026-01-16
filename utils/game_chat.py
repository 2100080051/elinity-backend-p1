from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.chat import Group, GroupMember
from datetime import datetime

async def create_game_chat_group(db: AsyncSession, session_id: str, host_id: str = None) -> str:
    """
    Creates a dedicated chat group for a game session.
    Returns the group_id.
    """
    # Create deterministic or unique name
    group_name = f"game_{session_id}"
    
    # Check if exists (idempotency)
    result = await db.execute(select(Group).where(Group.name == group_name))
    existing = result.scalars().first()
    if existing:
        return existing.id
        
    # Create Group
    # tenant owner is the host or a system default if None
    owner = host_id if host_id else "system"
    
    if owner == "system":
        t_sys = await db.execute(select(Tenant).where(Tenant.id == "system"))
        if not t_sys.scalars().first():
             try:
                 sys_user = Tenant(id="system", email="system@elinity.ai", password="sys", role="admin")
                 db.add(sys_user)
                 await db.commit()
             except: pass
    
    # Auto-ensure tenant exists (Guest Logic) to prevent FK errors
    if host_id:
        print(f"DEBUG: Checking existence of host_id={host_id}")
        from models.user import Tenant
        t_res = await db.execute(select(Tenant).where(Tenant.id == host_id))
        if not t_res.scalars().first():
            print(f"DEBUG: host_id={host_id} NOT FOUND. Creating guest...")
            try:
                guest = Tenant(id=host_id, email=f"guest_{host_id}@elinity.ai", password="guest", role="user")
                db.add(guest)
                await db.commit() # FORCE COMMIT
                await db.refresh(guest)
                print(f"DEBUG: Created Guest Host: {host_id}")
            except Exception as e:
                print(f"DEBUG: Failed to create guest host: {e}")
                # Try to rollback only if needed, but we want to proceed?
                # actually if this fails, the next step will fail too.
                # maybe race condition? check again?
                pass
        else:
            print(f"DEBUG: host_id={host_id} already exists.")

    group = Group(
        name=group_name,
        tenant=owner,
        description=f"Chat for Game Session {session_id}",
        type="group", # Must be one of allowed types
        created_at=datetime.utcnow()
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    
    # Add host as member if provided
    if host_id:
        member = GroupMember(
            group=group.id,
            tenant=host_id,
            role="admin",
            created_at=datetime.utcnow()
        )
        db.add(member)
        await db.commit()
        
    return group.id

async def add_player_to_game_chat(db: AsyncSession, group_id: str, user_id: str):
    """Adds a player to the game chat group."""
    # Check if already member
    result = await db.execute(select(GroupMember).where(
        GroupMember.group == group_id, 
        GroupMember.tenant == user_id
    ))
    existing = result.scalars().first()
    
    if not existing:
        member = GroupMember(
            group=group_id,
            tenant=user_id,
            role="member",
            created_at=datetime.utcnow()
        )
        db.add(member)
        await db.commit()
