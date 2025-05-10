from database.repository.session_manager import Repository
from database.models.team_member import TeamMember
from typing import Optional, List
from database.dtos import TeamMemberDTO
import discord


class TeamMemberRepository(Repository):
    def __init__(self):
        super().__init__(model_class=TeamMember)
        
    def get_by_user_id(self, user_id: int) -> Optional[TeamMemberDTO]:
        with self.session_scope() as session:
            query_set = session.query(self.model_class).filter(self.model_class.user_id == user_id).first()
            
            if not query_set:
                return None

            return TeamMemberDTO(**query_set.__dict__)
        
    def get_by_team_id(self, team_id: int) -> Optional[List[TeamMemberDTO]]:
        with self.session_scope() as session:
            query_set = session.query(self.model_class).filter(self.model_class.team_id == team_id).all()
            return [TeamMemberDTO(**member.__dict__) for member in query_set]