from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.models.scrim import Scrim
from database.db import get_db_session
from database.dtos import ScrimDTO
from database.repository.session_manager import Repository

class ScrimRepository(Repository):
    def __init__(self):
        super().__init__(Scrim)
    
    def _entity_to_dto(self, scrim_entity):
        """Convert a Scrim entity to ScrimDTO"""
        if not scrim_entity:
            return None
            
        return ScrimDTO(
            scrim_id=scrim_entity.scrim_id,
            creator_id=scrim_entity.creator_id,
            creator_team_id=scrim_entity.creator_team_id,
            scrim_type=scrim_entity.scrim_type,
            server_code=scrim_entity.server_code,
            scheduled_time=scrim_entity.scheduled_time,
            status=scrim_entity.status,
            message_id=scrim_entity.message_id,
            channel_id=scrim_entity.channel_id,
            team_size=scrim_entity.team_size,
            opponent_id=scrim_entity.opponent_id,
            opponent_team_id=scrim_entity.opponent_team_id,
            created_at=scrim_entity.created_at,
            matched_at=scrim_entity.matched_at,
            notes=scrim_entity.notes
        )

    def create_scrim(self, creator_id, scrim_type, server_code=None, scheduled_time=None, 
                    creator_team_id=None, team_size=5, notes=None):
        """Create a new scrim advertisement"""
        with self.session_scope() as session:
            scrim = Scrim(
                creator_id=creator_id,
                creator_team_id=creator_team_id,
                scrim_type=scrim_type,
                server_code=server_code,
                scheduled_time=scheduled_time,
                status='open',
                team_size=team_size,
                notes=notes
            )
            session.add(scrim)
            session.flush()  # To get the ID
            session.refresh(scrim)
            return self._entity_to_dto(scrim)

    def get_scrim_by_id(self, scrim_id):
        """Get a scrim by its ID"""
        with self.session_scope() as session:
            scrim = session.query(Scrim).filter(Scrim.scrim_id == scrim_id).first()
            return self._entity_to_dto(scrim)
    
    def get_scrim_by_message(self, message_id):
        """Get a scrim by its message ID"""
        with self.session_scope() as session:
            scrim = session.query(Scrim).filter(Scrim.message_id == message_id).first()
            return self._entity_to_dto(scrim)
    
    def update_scrim_message(self, scrim_id, message_id, channel_id):
        """Update the message ID and channel ID for a scrim"""
        with self.session_scope() as session:
            scrim = session.query(Scrim).filter(Scrim.scrim_id == scrim_id).first()
            if scrim:
                scrim.message_id = message_id
                scrim.channel_id = channel_id
                return True
            return False

    def get_open_scrims(self):
        """Get all scrims with open status"""
        with self.session_scope() as session:
            scrims = session.query(Scrim).filter(Scrim.status == 'open').all()
            return [self._entity_to_dto(scrim) for scrim in scrims]

    def match_scrims(self, scrim_id, opponent_id, opponent_team_id=None):
        """Match a scrim with an opponent"""
        with self.session_scope() as session:
            scrim = session.query(Scrim).filter(Scrim.scrim_id == scrim_id).first()
            if scrim and scrim.status == 'open':
                scrim.opponent_id = opponent_id
                scrim.opponent_team_id = opponent_team_id
                scrim.status = 'matched'
                scrim.matched_at = datetime.now()
                session.flush()
                session.refresh(scrim)
                return self._entity_to_dto(scrim)
            return None

    def cancel_scrim(self, scrim_id):
        """Cancel a scrim"""
        with self.session_scope() as session:
            scrim = session.query(Scrim).filter(Scrim.scrim_id == scrim_id).first()
            if scrim and scrim.status == 'open':
                scrim.status = 'cancelled'
                return True
            return False

    def get_user_scrims(self, user_id):
        """Get all scrims created by or joined by a user"""
        with self.session_scope() as session:
            scrims = session.query(Scrim).filter(
                ((Scrim.creator_id == user_id) | (Scrim.opponent_id == user_id))
            ).all()
            return [self._entity_to_dto(scrim) for scrim in scrims]

    def complete_scrim(self, scrim_id):
        """Mark a scrim as completed"""
        with self.session_scope() as session:
            scrim = session.query(Scrim).filter(Scrim.scrim_id == scrim_id).first()
            if scrim and scrim.status == 'matched':
                scrim.status = 'completed'
                return True
            return False

    def leave_queue(self, user_id):
        """Remove a user from all open scrims they've joined"""
        with self.session_scope() as session:
            scrims = session.query(Scrim).filter(
                (Scrim.opponent_id == user_id) & (Scrim.status == 'matched')
            ).all()
            
            count = 0
            for scrim in scrims:
                scrim.opponent_id = None
                scrim.opponent_team_id = None
                scrim.status = 'open'
                scrim.matched_at = None
                count += 1
            
            return count

    def get_team_scrims(self, team_id):
        """Get all scrims created by or joined by a team"""
        with self.session_scope() as session:
            scrims = session.query(Scrim).filter(
                ((Scrim.creator_team_id == team_id) | (Scrim.opponent_team_id == team_id))
            ).all()
            return [self._entity_to_dto(scrim) for scrim in scrims]
