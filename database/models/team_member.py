from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, func, Enum
import enum
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class RoleType(enum.Enum):
    captain = 'captain'
    vice_captain = 'vice_captain'
    member = 'member'

class TeamMember(Base):
    __tablename__ = 'team_members'
    
    team_id = Column(Integer, ForeignKey('teams.team_id'), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
    role = Column(Enum(RoleType), nullable=False, default=RoleType.member)
    team_display_name = Column(String(100), nullable=False)  # in-game name
    joined_at = Column(DateTime, server_default=func.now())
    rating = Column(Integer, nullable=True)  # Player rating out of 5 (can be null for regular players)
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"