from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.database import Base
from datetime import datetime

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    state = Column(String)  # e.g., "awaiting_email"
    fields = Column(Text)   # store all collected data as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
