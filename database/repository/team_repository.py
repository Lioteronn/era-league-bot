from database.repository.session_manager import Repository
from database.models.team import Team
from database.dtos import TeamDTO
from typing import Optional, List
from copy import deepcopy
import discord


class TeamRepository(Repository):
    """Repository for Team model operations."""
    def __init__(self):
        """Initialize with the Team model."""
        super().__init__(model_class=Team)
        
    def get_by_id(self, id: int) -> Optional[TeamDTO]:
        """
        Get a team by its ID.
        
        Args:
            id: The ID of the team to retrieve
            
        Returns:
            The team with the given ID as a DTO, or None if not found
        """
        with self.session_scope() as session:
            team = session.query(self.model_class).filter(self.model_class.team_id == id).first()
            if team:
                return TeamDTO(**team.__dict__)
            return None
        
    async def create(self, create_role_func: callable, ctx: discord.ApplicationContext, **kwargs) -> Optional[TeamDTO]:
        if self.get_by_name(kwargs['name']):
            return None
        
        with self.session_scope() as session:
            team = Team(**kwargs)
            role_id = await create_role_func(ctx, team)
            team.team_role_id = role_id
            session.add(team)
            session.flush()  # Flush to get the ID
            # Return a DTO to avoid detached instance errors
            return TeamDTO(**team.__dict__)
        
    def get_by_name(self, name: str) -> Optional[TeamDTO]:
        """
        Get a team by its name.
        
        Args:
            name: The name of the team to retrieve
            
        Returns:
            The team with the given name as a DTO, or None if not found
        """
        with self.session_scope() as session:
            team = session.query(self.model_class).filter(self.model_class.name == name).first()
            if team:
                return TeamDTO(**team.__dict__)
            return None
    
    def get_all(self, limit: Optional[int] = None) -> List[TeamDTO]:
        """
        Get all teams from the database.
        
        Args:
            limit: Optional limit on the number of teams to return
            
        Returns:
            List of all teams as DTOs
        """
        with self.session_scope() as session:
            query = session.query(self.model_class)
            if limit:
                query = query.limit(limit)
                
            teams = query.all()
            return [TeamDTO(**team.__dict__) for team in teams]
