from database.repository.session_manager import Repository
from database.models.server_config import ServerConfig
from typing import Optional, Dict, Any, List
from database.dtos import ServerConfigDTO


class ServerConfigRepository(Repository):
    def __init__(self):
        super().__init__(model_class=ServerConfig)
    
    def get_by_guild_id(self, guild_id: int) -> Optional[ServerConfigDTO]:
        """
        Get server configuration for a guild by its ID.
        
        Args:
            guild_id: The Discord guild ID
            
        Returns:
            Server configuration as a DTO, or None if not found
        """
        with self.session_scope() as session:
            config = session.query(self.model_class).filter(
                self.model_class.server_id == guild_id
            ).first()
            
            if not config:
                return None
                
            return ServerConfigDTO(**config.__dict__)
    
    def create_or_update(self, guild_id: int, **kwargs) -> ServerConfigDTO:
        """
        Create or update server configuration for a guild.
        
        Args:
            guild_id: The Discord guild ID
            **kwargs: Configuration fields to update
            
        Returns:
            Updated server configuration as a DTO
        """
        with self.session_scope() as session:
            config = session.query(self.model_class).filter(
                self.model_class.server_id == guild_id
            ).first()
            
            if not config:
                config = self.model_class(server_id=guild_id)
                session.add(config)
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            session.flush()
            
            return ServerConfigDTO(**config.__dict__)
    
    def set_approval_channel(self, guild_id: int, channel_id: int) -> ServerConfigDTO:
        """
        Set the team invitation approval channel for a guild.
        
        Args:
            guild_id: The Discord guild ID
            channel_id: The Discord channel ID
            
        Returns:
            Updated server configuration as a DTO
        """
        return self.create_or_update(guild_id, team_invite_approval_channel_id=channel_id)
