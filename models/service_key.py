from datetime import datetime
from sqlalchemy import Column, String, DateTime
import uuid
from database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class ServiceKey(Base):
    __tablename__ = "service_keys"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=True)
    key_hash = Column(String, nullable=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
