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
            query_set = (session.query(self.model_class)
                .filter(self.model_class.team_id == team_id)
                .order_by(self.model_class.role.asc())
                .all())
            
            return [TeamMemberDTO(**member.__dict__) for member in query_set]
    
    def update_role(self, team_id: int, user_id: int, role: str) -> Optional[TeamMemberDTO]:
        """
        Update the role of a team member without attempting to change primary key fields.
        
        Args:
            team_id: The team ID (part of primary key)
            user_id: The user ID (part of primary key)
            role: The new role to assign
            
        Returns:
            Updated TeamMemberDTO or None if not found
        """
        with self.session_scope() as session:
            # Find the member using both primary key fields
            member = session.query(self.model_class).filter(
                self.model_class.team_id == team_id,
                self.model_class.user_id == user_id
            ).first()
            
            if not member:
                return None
                
            # Update only the role field
            member.role = role
            session.flush()
            
            # Return a DTO to avoid detached instance errors
            return TeamMemberDTO(**member.__dict__)
            
    def set_player_rating(self, user_id: int, rating: float) -> Optional[TeamMemberDTO]:
        """
        Set a player's star rating (0-5)
        
        Args:
            user_id: The user ID to rate
            rating: The rating to assign (0-5, can use half stars like 3.5)
            
        Returns:
            Updated TeamMemberDTO or None if not found
        """
        # Convert the rating to an integer between 0 and 10 (so we can store half stars)
        db_rating = min(max(int(rating * 2), 0), 10)
        
        with self.session_scope() as session:
            # Find the team member by user_id (we assume a user can only be in one team)
            member = session.query(self.model_class).filter(
                self.model_class.user_id == user_id
            ).first()
            
            if not member:
                return None
                
            # Update the rating field
            member.rating = db_rating
            session.flush()
            
            # Return a DTO to avoid detached instance errors
            return TeamMemberDTO(**member.__dict__)
