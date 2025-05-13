import discord
from typing import Optional, Callable, Any, Dict
from database.models.invitation import InvitationStatus


class PlayerInviteView(discord.ui.View):
    def __init__(self, invitation_data: Dict[str, Any], callback: Callable):
        """
        View to handle player accepting or declining team invitation in DMs
        
        Args:
            invitation_data: Dictionary containing invitation details
            callback: Function to call when a button is pressed
        """
        super().__init__(timeout=None)
        self.invitation_data = invitation_data
        self.callback = callback
        self.invitation_id = invitation_data.get('invitation_id')
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Check if the user interacting with the view is the target user
        """
        # Only allow the invited user to interact with these buttons
        if interaction.user.id != self.invitation_data.get('user_id'):
            await interaction.response.send_message("This invitation is not for you.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self) -> None:
        """
        Handle view timeout
        """
        # Mark invitation as expired in the callback
        await self.callback(self.invitation_id, InvitationStatus.expired, None)
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, custom_id="accept_button")
    async def accept_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("You've accepted the team invitation!", ephemeral=True)
        await self.callback(self.invitation_id, InvitationStatus.accepted, interaction)
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, custom_id="decline_button")
    async def decline_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("You've declined the team invitation.", ephemeral=True)
        await self.callback(self.invitation_id, InvitationStatus.declined, interaction)


class AdminApprovalView(discord.ui.View):
    def __init__(self, invitation_data: Dict[str, Any], callback: Callable):
        """
        View for admins to approve or reject a team invitation in the approval channel
        
        Args:
            invitation_data: Dictionary containing invitation details
            callback: Function to call when a button is pressed
        """
        super().__init__(timeout=None)
        self.invitation_data = invitation_data
        self.callback = callback
        self.invitation_id = invitation_data.get('invitation_id')
        self.rejection_modal = None
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Check if the user interacting with the view has admin permissions
        """
        # This will be enhanced in the team_commands cog to check for admin role
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to approve team invitations.", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, custom_id="approve_button")
    async def approve_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Send a temporary response
        await interaction.response.send_message("Processing approval...", ephemeral=True)
        # Let the callback know we've already responded
        await self.callback(self.invitation_id, True, interaction)
    
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="reject_button")
    async def reject_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Create rejection modal
        self.rejection_modal = RejectionReasonModal(self.invitation_id, self.callback)
        await interaction.response.send_modal(self.rejection_modal)


class RejectionReasonModal(discord.ui.Modal):
    def __init__(self, invitation_id: int, callback: Callable):
        super().__init__(title="Provide Rejection Reason")
        self.invitation_id = invitation_id
        self.callback = callback
        
        self.reason = discord.ui.InputText(
            label="Reason for rejection",
            placeholder="Please provide a reason for rejecting this invitation",
            style=discord.InputTextStyle.paragraph,
            required=True,
            max_length=1000
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason.value
        await interaction.response.send_message("Invitation rejected with reason provided.", ephemeral=True)
        await self.callback(self.invitation_id, False, interaction, reason)
