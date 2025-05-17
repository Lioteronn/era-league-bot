from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, BigInteger, Text
from sqlalchemy.orm import relationship
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class Scrim(Base):
    __tablename__ = 'scrims'
    
    scrim_id = Column(Integer, primary_key=True)
    # The Discord user ID who created the scrim ad
    creator_id = Column(BigInteger, nullable=False)
    # The team ID of the creator (if applicable)
    creator_team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=True)
    # Type of scrim: 'now' or 'scheduled'
    scrim_type = Column(String(20), nullable=False)
    # Server code for immediate scrims or scheduled ones with a code
    server_code = Column(String(50), nullable=True)
    # Time for scheduled scrims (stored as string for now, can be converted to DateTime later)
    scheduled_time = Column(String(100), nullable=True)
    # Status: 'open', 'matched', 'completed', 'cancelled'
    status = Column(String(20), default='open')
    # ID of the Discord message containing the scrim ad
    message_id = Column(BigInteger, nullable=True)
    # Channel where the ad was posted
    channel_id = Column(BigInteger, nullable=True)
    # Team size (optional parameter for future extension)
    team_size = Column(Integer, default=5)
    # The team/user that accepted the scrim
    opponent_id = Column(BigInteger, nullable=True)
    # The team ID of the opponent (if applicable)
    opponent_team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=True)
    # When the scrim was created
    created_at = Column(DateTime, server_default=func.now())
    # When the scrim was matched (if applicable)
    matched_at = Column(DateTime, nullable=True)
    # Additional notes or requirements
    notes = Column(Text, nullable=True)
    
    # Relationships (if needed)
    creator_team = relationship('Team', foreign_keys=[creator_team_id], back_populates='created_scrims')
    opponent_team = relationship('Team', foreign_keys=[opponent_team_id], back_populates='joined_scrims')
    
    def __repr__(self):
        return f"<Scrim(scrim_id={self.scrim_id}, type={self.scrim_type}, status={self.status})>"
