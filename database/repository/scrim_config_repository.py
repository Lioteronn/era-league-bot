from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.models.scrim_config import ScrimConfig
from database.db import get_db_session
from database.dtos import ScrimConfigDTO

class ScrimConfigRepository:
    def __init__(self, session: Session = None):
        self.session = session if session else get_db_session()
    
    def _entity_to_dto(self, config_entity):
        """Convert a ScrimConfig entity to ScrimConfigDTO"""
        if not config_entity:
            return None
            
        return ScrimConfigDTO(
            config_id=config_entity.config_id,
            guild_id=config_entity.guild_id,
            scrim_channel_id=config_entity.scrim_channel_id,
            cooldown_minutes=config_entity.cooldown_minutes,
            auto_expire_hours=config_entity.auto_expire_hours,
            enabled=config_entity.enabled,
            settings=config_entity.settings,
            created_at=config_entity.created_at,
            updated_at=config_entity.updated_at
        )

    def get_config(self, guild_id):
        """Get scrim configuration for a guild"""
        config = self.session.query(ScrimConfig).filter(ScrimConfig.guild_id == guild_id).first()
        
        # If config doesn't exist, create a default one
        if not config:
            config = ScrimConfig(guild_id=guild_id)
            self.session.add(config)
            self.session.commit()
        
        return self._entity_to_dto(config)
    
    def update_channel(self, guild_id, channel_id):
        """Set the channel for scrim advertisements"""
        config = self.session.query(ScrimConfig).filter(ScrimConfig.guild_id == guild_id).first()
        
        if not config:
            config = ScrimConfig(guild_id=guild_id, scrim_channel_id=channel_id)
            self.session.add(config)
        else:
            config.scrim_channel_id = channel_id
        
        self.session.commit()
        return self._entity_to_dto(config)
    
    def update_cooldown(self, guild_id, cooldown_minutes):
        """Set the cooldown between scrim ads"""
        config = self.session.query(ScrimConfig).filter(ScrimConfig.guild_id == guild_id).first()
        
        if not config:
            config = ScrimConfig(guild_id=guild_id, cooldown_minutes=cooldown_minutes)
            self.session.add(config)
        else:
            config.cooldown_minutes = cooldown_minutes
        
        self.session.commit()
        return self._entity_to_dto(config)
    
    def update_auto_expire(self, guild_id, auto_expire_hours):
        """Set the auto-expire time for scrim ads"""
        config = self.session.query(ScrimConfig).filter(ScrimConfig.guild_id == guild_id).first()
        
        if not config:
            config = ScrimConfig(guild_id=guild_id, auto_expire_hours=auto_expire_hours)
            self.session.add(config)
        else:
            config.auto_expire_hours = auto_expire_hours
        
        self.session.commit()
        return self._entity_to_dto(config)
    
    def set_enabled(self, guild_id, enabled):
        """Enable or disable the scrim system"""
        config = self.session.query(ScrimConfig).filter(ScrimConfig.guild_id == guild_id).first()
        
        if not config:
            config = ScrimConfig(guild_id=guild_id, enabled=enabled)
            self.session.add(config)
        else:
            config.enabled = enabled
        
        self.session.commit()
        return self._entity_to_dto(config)
