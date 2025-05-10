from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, BigInteger
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class Team(Base):
    __tablename__ = 'teams'
    
    team_id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    hexcode = Column(String(7))
    logo_path = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    active = Column(Boolean, default=True)
    team_captain_id = Column(BigInteger, default=None)
    team_role_id = Column(BigInteger, default=None)
    
    def __repr__(self):
        return f"<Team(team_id={self.team_id}, name={self.name})>"