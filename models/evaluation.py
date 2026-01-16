from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from database.session import Base


class EvaluationReport(Base):
    __tablename__ = "evaluation_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=True)
    skill_id = Column(String, nullable=True)
    skill_type = Column(String, nullable=True)
    evaluation_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
