from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, func, Boolean
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)  # Discord user ID
    username = Column(String(100), nullable=False)
    display_name = Column(String(100))
    joined_at = Column(DateTime, server_default=func.now())
    is_roblox_verified = Column(Boolean, default=False)
    roblox_username = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"