from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime, JSON
from sqlalchemy.sql import func
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class Guild(Base):
    __tablename__ = 'guilds'
    
    id = Column(BigInteger, primary_key=True)  # Discord guild ID
    name = Column(String(100))
    owner_id = Column(BigInteger)
    prefix = Column(String(10), default='!')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Guild(id={self.id}, name={self.name})>"