from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, func, Enum
import enum
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class InvitationStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    declined = 'declined'
    expired = 'expired'

class Invitation(Base):
    __tablename__ = 'invitations'
    
    invitation_id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    inviter_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.pending, nullable=False)
    
    def __repr__(self):
        return f"<Invitation(invitation_id={self.invitation_id}, team_id={self.team_id}, user_id={self.user_id}, status={self.status})>"