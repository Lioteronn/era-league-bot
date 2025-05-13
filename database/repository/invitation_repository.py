from database.repository.session_manager import Repository
from database.models.invitation import Invitation, InvitationStatus
from typing import Optional, List
from database.dtos import InvitationDTO
import datetime


class InvitationRepository(Repository):
    def __init__(self):
        super().__init__(model_class=Invitation)
        
    def create(self, team_id: int, user_id: int, inviter_id: int, expires_in_days: int = 7) -> InvitationDTO:
        """
        Create a new invitation for a user to join a team.
        
        Args:
            team_id: The ID of the team
            user_id: The Discord ID of the user being invited
            inviter_id: The Discord ID of the user who sent the invitation
            expires_in_days: Number of days until the invitation expires
            
        Returns:
            The created invitation as a DTO
        """
        expires_at = datetime.datetime.now() + datetime.timedelta(days=expires_in_days)
        
        with self.session_scope() as session:
            invitation = self.model_class(
                team_id=team_id,
                user_id=user_id,
                inviter_id=inviter_id,
                expires_at=expires_at,
                status=InvitationStatus.pending
            )
            session.add(invitation)
            session.flush()
            
            # Create DTO from the added invitation
            invitation_dict = invitation.__dict__.copy()
            return InvitationDTO(**invitation_dict)
    
    def get_by_id(self, invitation_id: int) -> Optional[InvitationDTO]:
        """
        Get an invitation by its ID.
        
        Args:
            invitation_id: The ID of the invitation
            
        Returns:
            The invitation as a DTO, or None if not found
        """
        with self.session_scope() as session:
            invitation = session.query(self.model_class).filter(
                self.model_class.invitation_id == invitation_id
            ).first()
            
            if not invitation:
                return None
                
            return InvitationDTO(**invitation.__dict__)
    
    def get_pending_by_user_id(self, user_id: int) -> List[InvitationDTO]:
        """
        Get all pending invitations for a user.
        
        Args:
            user_id: The Discord ID of the user
            
        Returns:
            A list of pending invitations as DTOs
        """
        with self.session_scope() as session:
            invitations = session.query(self.model_class).filter(
                self.model_class.user_id == user_id,
                self.model_class.status == InvitationStatus.pending
            ).all()
            
            return [InvitationDTO(**inv.__dict__) for inv in invitations]
    
    def get_pending_by_inviter_id(self, inviter_id: int) -> List[InvitationDTO]:
        """
        Get all pending invitations sent by a user.
        
        Args:
            inviter_id: The Discord ID of the inviter
            
        Returns:
            A list of pending invitations as DTOs
        """
        with self.session_scope() as session:
            invitations = session.query(self.model_class).filter(
                self.model_class.inviter_id == inviter_id,
                self.model_class.status == InvitationStatus.pending
            ).all()
            
            return [InvitationDTO(**inv.__dict__) for inv in invitations]
    
    def get_pending_by_team_id(self, team_id: int) -> List[InvitationDTO]:
        """
        Get all pending invitations for a team.
        
        Args:
            team_id: The ID of the team
            
        Returns:
            A list of pending invitations as DTOs
        """
        with self.session_scope() as session:
            invitations = session.query(self.model_class).filter(
                self.model_class.team_id == team_id,
                self.model_class.status == InvitationStatus.pending
            ).all()
            
            return [InvitationDTO(**inv.__dict__) for inv in invitations]
    
    def update_status(self, invitation_id: int, status: InvitationStatus) -> Optional[InvitationDTO]:
        """
        Update the status of an invitation.
        
        Args:
            invitation_id: The ID of the invitation
            status: The new status
            
        Returns:
            The updated invitation as a DTO, or None if not found
        """
        with self.session_scope() as session:
            invitation = session.query(self.model_class).filter(
                self.model_class.invitation_id == invitation_id
            ).first()
            
            if not invitation:
                return None
                
            invitation.status = status
            session.flush()
            
            return InvitationDTO(**invitation.__dict__)
