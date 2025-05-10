from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, func, Enum, JSON
import enum
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class ActionType(enum.Enum):
    invite = 'invite'
    join = 'join'
    kick = 'kick'
    leave = 'leave'
    name_change = 'name_change'
    role_change = 'role_change'
    team_create = 'team_create'
    team_disband = 'team_disband'

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    action_type = Column(Enum(ActionType), nullable=False)
    actor_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, action_type={self.action_type}, team_id={self.team_id})>"