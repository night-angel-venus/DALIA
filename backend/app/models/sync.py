from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from app.database import Base


class SyncLogs(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_event_id = Column(String(36), unique=True, nullable=False, index=True)
    dtr_id = Column(Integer, ForeignKey("dtr.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    