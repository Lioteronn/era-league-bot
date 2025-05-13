from sqlalchemy import Column, BigInteger, DateTime, JSON, func
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import Base

class ServerConfig(Base):
    __tablename__ = 'server_config'
    
    server_id = Column(BigInteger, primary_key=True)  # Discord Guild ID
    log_channel_id = Column(BigInteger)
    transaction_channel_id = Column(BigInteger)
    bot_command_channel_id = Column(BigInteger)
    team_invite_approval_channel_id = Column(BigInteger)
    admin_role_ids = Column(JSON)  # Array or JSON of role IDs
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ServerConfig(server_id={self.server_id})>"