from database.repository.session_manager import Repository
from database.models.user import User
from typing import Optional, Dict, Any, List
from database.dtos import UserDTO
import discord


class UserRepository(Repository):
    def __init__(self):
        super().__init__(model_class=User)
    
    def get_by_id(self, user_id: int) -> Optional[UserDTO]:
        """
        Get a user by their Discord ID.
        
        Args:
            user_id: The Discord user ID
            
        Returns:
            The user as a DTO, or None if not found
        """
        with self.session_scope() as session:
            user = session.query(self.model_class).filter(
                self.model_class.user_id == user_id
            ).first()
            
            if not user:
                return None
                
            return UserDTO(**user.__dict__)
    
    def create(self, user_id: int, username: str, display_name: str, is_roblox_verified: bool = False, roblox_username: str = None) -> UserDTO:
        """
        Create a new user.
        
        Args:
            user_id: The Discord user ID
            username: The Discord username
            display_name: The Discord display name
            is_roblox_verified: Whether the user is verified with Roblox
            roblox_username: The Roblox username if verified
            
        Returns:
            The created user as a DTO
        """
        with self.session_scope() as session:
            user = self.model_class(
                user_id=user_id,
                username=username,
                display_name=display_name,
                is_roblox_verified=is_roblox_verified,
                roblox_username=roblox_username
            )
            session.add(user)
            session.flush()
            
            return UserDTO(**user.__dict__)
    
    def update(self, user_id: int, **kwargs) -> Optional[UserDTO]:
        """
        Update a user.
        
        Args:
            user_id: The Discord user ID
            **kwargs: Fields to update
            
        Returns:
            The updated user as a DTO, or None if not found
        """
        with self.session_scope() as session:
            user = session.query(self.model_class).filter(
                self.model_class.user_id == user_id
            ).first()
            
            if not user:
                return None
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            session.flush()
            
            return UserDTO(**user.__dict__)
    
    def update_roblox_verification(self, user_id: int, is_verified: bool, roblox_username: str = None) -> Optional[UserDTO]:
        """
        Update a user's Roblox verification status.
        
        Args:
            user_id: The Discord user ID
            is_verified: Whether the user is verified with Roblox
            roblox_username: The Roblox username if verified
            
        Returns:
            The updated user as a DTO, or None if not found
        """
        return self.update(
            user_id=user_id,
            is_roblox_verified=is_verified,
            roblox_username=roblox_username
        )

    def set_player_rating(self, user_id: int, rating: float) -> Optional[UserDTO]:
        """
        Set a player's star rating (0-5)
        
        Args:
            user_id: The user ID to rate
            rating: The rating to assign (0-5, can use half stars like 3.5)
            
        Returns:
            Updated UserDTO or None if not found
        """
        # Convert the rating to an integer between 0 and 10 (so we can store half stars)
        db_rating = min(max(int(rating * 2), 0), 10)
        
        return self.update(
            user_id=user_id,
            rating=db_rating
        )
        
    def set_player_position(self, user_id: int, position: str) -> Optional[UserDTO]:
        """
        Set a player's position
        
        Args:
            user_id: The user ID
            position: The position name (must match a PositionType enum value)
            
        Returns:
            Updated UserDTO or None if not found
        """
        from database.models.user import PositionType
        
        # Validate the position against the enum
        try:
            position_enum = PositionType[position.lower().replace(' ', '_')]
            return self.update(
                user_id=user_id,
                position=position_enum
            )
        except KeyError:
            # Invalid position name
            return None
            
    def get_top_players_by_position(self, position: str, limit: int = 10) -> List[UserDTO]:
        """
        Get the top-rated players for a specific position.
        
        Args:
            position: Position to filter by (must match a PositionType enum value)
            limit: Maximum number of players to return
            
        Returns:
            List of UserDTOs sorted by rating (highest first)
        """
        from database.models.user import PositionType
        
        # Validate the position against the enum
        try:
            position_enum = PositionType[position.lower().replace(' ', '_')]
            
            with self.session_scope() as session:
                users = session.query(self.model_class).filter(
                    self.model_class.position == position_enum,
                    self.model_class.rating.isnot(None)  # Only include rated players
                ).order_by(
                    self.model_class.rating.desc()  # Sort by rating, highest first
                ).limit(limit).all()
                
                return [UserDTO(**user.__dict__) for user in users]
        except KeyError:
            # Invalid position name
            return []
    
    def get_by_roblox_username(self, roblox_username: str) -> Optional[UserDTO]:
        """
        Get a user by their Roblox username.
        
        Args:
            roblox_username: The Roblox username
            
        Returns:
            The user as a DTO, or None if not found
        """
        with self.session_scope() as session:
            user = session.query(self.model_class).filter(
                self.model_class.username == roblox_username
            ).first()
            
            if not user:
                return None
                
            return UserDTO(**user.__dict__)
        
    def delete_by_user_id_or_roblox_username(self, user_id: int = None, roblox_username: str = None) -> bool:
        """
        Delete a user by their Discord user ID or Roblox username.
        
        Args:
            user_id: The Discord user ID
            roblox_username: The Roblox username
            
        Returns:
            True if deleted, False if not found
        """
        with self.session_scope() as session:
            user = session.query(self.model_class).filter(
                or_(
                    self.model_class.user_id == user_id,
                    self.model_class.username == roblox_username
                )
            ).first()
            
            if not user:
                return False
                
            session.delete(user)
            return True