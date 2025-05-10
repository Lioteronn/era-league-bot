from database.repository.session_manager import db_session, Repository
from database.models.team import Team
from typing import Optional
from copy import deepcopy
import discord


class TeamRepository(Repository):
    """Repository for Team model operations."""
    def __init__(self):
        """Initialize with the Team model."""
        super().__init__(model_class=Team)
        
    async def create(self, create_role_func: callable, ctx: discord.ApplicationContext, **kwargs) -> Team:
        if self.get_by_name(kwargs['name']):
            return None
        
        with self.session_scope() as session:
            team = Team(**kwargs)
            role_id = await create_role_func(ctx, team)
            team.team_role_id = role_id
            session.add(team)
            team_copy = deepcopy(team)
            return team_copy
        
    def get_by_name(self, name: str) -> Optional[Team]:
        """
        Get a team by its name.
        
        Args:
            name: The name of the team to retrieve
            
        Returns:
            Team instance or None if not found
        """
        with self.session_scope() as session:
            team = deepcopy(session.query(Team).filter(Team.name == name).first())
            return team
