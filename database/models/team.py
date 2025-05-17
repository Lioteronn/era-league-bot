from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, BigInteger
from sqlalchemy.orm import relationship
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
    
    # Relationships with scrims
    created_scrims = relationship('Scrim', foreign_keys='Scrim.creator_team_id', back_populates='creator_team')
    joined_scrims = relationship('Scrim', foreign_keys='Scrim.opponent_team_id', back_populates='opponent_team')
    
    def __repr__(self):
        return f"<Team(team_id={self.team_id}, name={self.name})>"