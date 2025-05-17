from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, BigInteger, JSON
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class ScrimConfig(Base):
    __tablename__ = 'scrim_configs'
    
    config_id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    scrim_channel_id = Column(BigInteger, nullable=True)  # Channel for scrim ads
    cooldown_minutes = Column(Integer, default=60)  # Cooldown between scrim ads
    auto_expire_hours = Column(Integer, default=24)  # Auto-expire time for scrim ads
    enabled = Column(Boolean, default=True)  # Is the scrim system enabled
    settings = Column(JSON, default={})  # Additional settings as JSON
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ScrimConfig(guild_id={self.guild_id}, enabled={self.enabled})>"
