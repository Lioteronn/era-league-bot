from re import S
import discord
from discord.ext import commands
from discord.commands import Option
from datetime import datetime
from typing import Union, Optional, Literal

# Import database repositories
from database.repository.team_repository import TeamRepository
from database.repository.team_member_repository import TeamMemberRepository
from database.repository.user_repository import UserRepository
from database.repository.invitation_repository import InvitationRepository
from database.repository.server_config_repository import ServerConfigRepository

# Import models and enums
from database.models.team_member import RoleType
from database.models.user import PositionType
from database.models.team import Team
from database.models.invitation import InvitationStatus

# Import verification decorator
from cogs.verification_commands import require_verification
from cogs.permissions.admin_checker import is_admin
from images.image_downloader import download_and_save_image
from cogs.views.invitation_views import PlayerInviteView, AdminApprovalView
import datetime

class TeamCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.team_repository = TeamRepository()
        self.team_member_repository = TeamMemberRepository()
        self.invitation_repository = InvitationRepository()
        self.server_config_repository = ServerConfigRepository()
        self.user_repository = UserRepository()
        # Cache to track pending invitations per inviter
        self.pending_invites_cache = {}
        # Maximum number of pending invitations allowed per captain/vice-captain
        self.max_pending_invites = 3

    @commands.slash_command(name="create-team", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    @require_verification()
    async def create_team(self, ctx: discord.ApplicationContext, team_name: str, hexcode: str, logo_url: str = None) -> None:
        """
        Create a new team with the specified name, hexcode, and logo URL.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team.
            hexcode (str): The hex code for the team's color. Defaults to None.
            logo_url (str: optional): The URL for the team's logo. Defaults to None.
        """
        # Check if the hexcode is valid
        if hexcode and not (len(hexcode) == 7 and hexcode.startswith("#")):
            await ctx.respond("Hex code must be in the format #RRGGBB.")
            return

        # Check if the logo URL is valid
        if logo_url and not logo_url.startswith(("http://", "https://")):
            await ctx.respond("Logo URL must start with http:// or https://.")
            return
        
        if not hexcode:
            await ctx.respond("Hex code is required.")
            return

        if not logo_url:
            logo_path = "images/nologo.png"
        else:
            logo_path = download_and_save_image(logo_url, team_name)

        team_obj = await self.team_repository.create(create_role_func=self._create_role,
                                               ctx=ctx,
                                               name=team_name, 
                                               hexcode=hexcode, 
                                               logo_path=logo_path)
        if not team_obj:
            await ctx.respond(f"Team '{team_name}' already exists.")
            return
        
        await ctx.respond(f"Team '{team_name}' created successfully!")

    # TODO: Set the user as captain, gotta make all the roblox verification system first and all that
    @commands.slash_command(name="set-captain", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    @require_verification("user")
    async def set_captain(self, ctx: discord.ApplicationContext, team_name: str, user: str) -> None:
        """
        Set the captain for the team.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team.
            user (str): The user to set as the captain.
        """
        await self._set_captainship(ctx, team_name, user, RoleType.captain)
    
    @commands.slash_command(name="set-vicecaptain", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    @require_verification("user")
    async def set_vicecaptain(self, ctx: discord.ApplicationContext, team_name: str, user: str) -> None:
        """
        Set the vicecaptain for the team.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team.
            user (str): The user to set as the vicecaptain.
        """
        await self._set_captainship(ctx, team_name, user, RoleType.vice_captain)

    async def _set_captainship(self, ctx: discord.ApplicationContext, team_name: str, user: str, role: RoleType) -> None:
        """
        Set the captain for the team.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team.
            user (str): The user to set as the captain.
        """
        team_obj = self.team_repository.get_by_name(team_name)
        if not team_obj:
            await ctx.respond(f"Team '{team_name}' not found.")
            return
        
        user = await ctx.guild.fetch_member(int(user) if not user.startswith("<@") else int(user[2:-1]))
        
        team_member = self.team_member_repository.get_by_user_id(user.id)
        if not team_member:
            await ctx.respond(f"User {user.mention} is not a member of any team.")
            return
        
        if team_member.team_id != team_obj.team_id:
            await ctx.respond(f"User {user.mention} is not a member of team '{team_name}'.")
            return
        
        if team_member.role == role:
            await ctx.respond(f"User {user.mention} is already the {role.name} of team '{team_name}'.")
            return
        
        # Update the team's captain_id field
        self.team_repository.update(team_id=team_obj.team_id, team_captain_id=team_member.user_id)
        
        # Use the specialized update_role method to avoid primary key constraint issues
        self.team_member_repository.update_role(team_id=team_obj.team_id, user_id=team_member.user_id, role=role)
        await ctx.respond(f"{role.name.title()} for team '{team_obj.name}' set to {user.mention}.")
        
    @commands.slash_command(name="search-team", guild_ids=[1370422733086658631])
    @require_verification()
    async def search_team(self, ctx: discord.ApplicationContext, team_name: str) -> None:
        """
        Search for a team by name.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team to search for.
        """
        team_obj = self.team_repository.get_by_name(team_name)
        if not team_obj:
            await ctx.respond(f"Team '{team_name}' not found.")
            return
        
        team_title = f"**{team_obj.name}**"
        team_role = ctx.guild.get_role(team_obj.team_role_id)
        file = discord.File(team_obj.logo_path, filename="logo.png")
        
        if not file:
            file = discord.File("images/nologo.png", filename="nologo.png")
            
        logo_url = "attachment://logo.png" if file else "attachment://nologo.png"

        embed = discord.Embed(
            title=team_title,
            description=f"",
            color=discord.Color(int(team_obj.hexcode[1:], 16))
        )
        embed.set_thumbnail(url=logo_url)
        embed.add_field(name="🔹 Current Roster", value=self._fetch_team_players(team_obj.team_id), inline=True)
        embed.add_field(name="🔹 Team Role", value=f"<@&{team_role.id}>", inline=True)
        await ctx.respond(embed=embed, files=[file])

    @commands.slash_command(name="force-add-player-to-team", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    @require_verification("user")
    async def force_add_player_to_team(self, ctx: discord.ApplicationContext, team_name: str, user: discord.Member) -> None:
        """
        Force add a player to a team.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team.
            user (discord.Member): The user to add to the team.
        """
        team_obj = self.team_repository.get_by_name(team_name)
        if not team_obj:
            await ctx.respond(f"Team '{team_name}' not found.")
            return
        
        team_member = self.team_member_repository.get_by_user_id(user.id)
        if team_member:
            await ctx.respond(f"User {user.mention} is already a member of team '{team_obj.name}'.")
            return
        
        self.team_member_repository.create(team_id=team_obj.team_id, user_id=user.id, role=RoleType.member, team_display_name=user.display_name)
        await user.add_roles(ctx.guild.get_role(team_obj.team_role_id))
        await ctx.respond(f"User {user.mention} added to team '{team_obj.name}'.")

    @commands.slash_command(name="set-player-rating", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    async def set_player_rating(self, ctx: discord.ApplicationContext, user: discord.Member, rating: float) -> None:
        """
        Set a player's star rating.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            user (discord.Member): The user to rate.
            rating (float): Rating from 0 to 5 stars (can use half stars like 3.5).
        """
        # First check if user exists in database
        user_obj = self.user_repository.get_by_id(user.id)
        if not user_obj:
            await ctx.respond(f"User {user.mention} does not exist in the database.", ephemeral=True)
            return
        
        # Set the rating in the User model
        updated_user = self.user_repository.set_player_rating(user.id, rating)
        if not updated_user:
            await ctx.respond(f"Failed to update rating for {user.mention}.", ephemeral=True)
            return
        
        # Format the stars for display
        star_display = self._format_rating_stars(updated_user.rating)
        await ctx.respond(f"Set {user.mention}'s rating to {star_display} ({rating}/5)")
        
    @commands.slash_command(name="set-player-position", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    async def set_player_position(self, ctx: discord.ApplicationContext, user: discord.Member, 
                                  position: Option(str, "Player position", 
                                                choices=[p.value for p in PositionType])) -> None:
        """
        Set a player's position.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            user (discord.Member): The user to set position for.
            position (str): The volleyball position.
        """
        # First check if user exists in database
        user_obj = self.user_repository.get_by_id(user.id)
        if not user_obj:
            await ctx.respond(f"User {user.mention} does not exist in the database.", ephemeral=True)
            return
        
        # Set the position in the User model
        updated_user = self.user_repository.set_player_position(user.id, position)
        if not updated_user:
            await ctx.respond(f"Failed to update position for {user.mention}.", ephemeral=True)
            return
        
        await ctx.respond(f"Set {user.mention}'s position to {position}")
        
    @commands.slash_command(name="top-players", guild_ids=[1370422733086658631])
    async def top_players(self, ctx: discord.ApplicationContext, 
                         position: Option(str, "Position to filter by", 
                                       choices=[p.value for p in PositionType]), 
                         limit: Option(int, "Number of players to show", min_value=1, max_value=25, default=10)) -> None:
        """
        Show top-rated players by position.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            position (str): The position to filter by.
            limit (int): Number of players to show (default 10).
        """
        # Get top players for the specified position
        top_players = self.user_repository.get_top_players_by_position(position.lower().replace(' ', '_'), limit)
        
        if not top_players:
            await ctx.respond(f"No rated players found for position: {position}", ephemeral=True)
            return
        
        # Build the embed for display
        embed = discord.Embed(
            title=f"Top {position} Players",
            description=f"The highest rated {position.lower()} players",
            color=discord.Color.gold()
        )
        
        # Add player entries to the embed
        for i, player in enumerate(top_players):
            # Format the rating as stars
            star_display = self._format_rating_stars(player.rating)
            
            # Format the player entry
            try:
                discord_user = await ctx.guild.fetch_member(player.user_id)
                player_name = discord_user.name
            except:
                # Use the database name if we can't fetch the member
                player_name = player.display_name or player.username
                
            embed.add_field(
                name=f"#{i+1}: {player_name}",
                value=f"Rating: {star_display} ({'5' if player.rating > 10 else float(player.rating/2)}/5)",
                inline=False
            )
            
        await ctx.respond(embed=embed)
        
    @commands.slash_command(name="list-teams", guild_ids=[1370422733086658631])
    @require_verification()
    async def list_teams(self, ctx: discord.ApplicationContext,
                        limit: Option(int, "Maximum number of teams to display", min_value=1, max_value=50, default=25)) -> None:
        """
        List all teams in the database with information about each team.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            limit (int): Maximum number of teams to display. Defaults to 25.
        """
        # Get all teams from the database with the optional limit
        teams = self.team_repository.get_all(limit=limit)
        
        if not teams:
            await ctx.respond("No teams found in the database.", ephemeral=True)
            return
        
        # Build the embed for display
        embed = discord.Embed(
            title="Teams List",
            description=f"Showing {len(teams)} teams",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        # Add team entries to the embed
        for team in teams:
            # Get all members of this team
            team_members = self.team_member_repository.get_by_team_id(team.team_id)
            total_players = len(team_members) if team_members else 0
            
            # Count star rated players (players with rating > 0)
            star_rated_players = sum(1 for member in team_members if member.rating is not None and member.rating > 0) if team_members else 0
            
            # Get team role mention
            role_mention = f"<@&{team.team_role_id}>" if team.team_role_id else "No role assigned"
            
            # Format team information
            value = f"**Total Players:** {total_players}\n**Team Role:** {role_mention}\n**Star Rated Players:** {star_rated_players}"
            
            embed.add_field(
                name=team.name,
                value=value,
                inline=True
            )
        
        await ctx.respond(embed=embed)
    
    def _fetch_team_players(self, team_id: int) -> str:
        roster_members = self.team_member_repository.get_by_team_id(team_id)
        if not roster_members:
            return "- No players added yet."
        
        roster_string = ""
        for member in roster_members:
            rating_display = ""
            if member.rating is not None:
                rating_display = f" {self._format_rating_stars(member.rating)} ({member.rating/2}/5)"
                
            if member.role == RoleType.captain:
                roster_string += f"- {member.team_display_name} (C){rating_display}\n"
            elif member.role == RoleType.vice_captain:
                roster_string += f"- {member.team_display_name} (VC){rating_display}\n"
            else:
                roster_string += f"- {member.team_display_name}{rating_display}\n"
        
        return roster_string
    
    async def _create_role(self, ctx: discord.ApplicationContext, team_obj: Team) -> int:
        """
        Create a new role for the team with the specified name and hexcode.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_obj (Team): The team object containing team information.
        """
        guild = ctx.guild
        role = await guild.create_role(
            name=team_obj.name,
            color=discord.Color(int(team_obj.hexcode[1:], 16)) if team_obj.hexcode else discord.Color.default(),
            hoist=True, # Make it show separately in the member list
            mentionable=True,
            reason=f"Team role for {team_obj.name}"
        )
        await ctx.respond(f"Team role '{role.name}' created successfully!")
        return role.id

    @commands.slash_command(name="register-approval-channel", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    @require_verification()
    async def register_approval_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel) -> None:
        """
        Register a channel for team invitation approvals.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            channel (discord.TextChannel): The channel to use for approvals.
        """
        config = self.server_config_repository.set_approval_channel(ctx.guild.id, channel.id)
        await ctx.respond(f"Team invitation approval channel set to {channel.mention}.", ephemeral=True)
        
    async def _verify_team_and_team_member(self, ctx: discord.ApplicationContext, team_name: str = None) -> tuple:
        """
        Auxiliary function to verify team existence and team member role.
        
        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str, optional): The name of the team. If None, attempts to find team based on user.
            
        Returns:
            tuple: (team_obj, team_member) if valid, (None, None) otherwise
        """
        # Get user's team if no team_name provided
        if team_name is None:
            team_member = self.team_member_repository.get_by_user_id(ctx.author.id)
            if not team_member:
                await ctx.respond("You are not a member of any team.", ephemeral=True)
                return None, None
                
            team_obj = self.team_repository.get_by_id(team_member.team_id)
        else:
            # Check if team exists
            team_obj = self.team_repository.get_by_name(team_name)
            if not team_obj:
                await ctx.respond(f"Team '{team_name}' not found.", ephemeral=True)
                return None, None
                
            # Check if user is a team member
            team_member = self.team_member_repository.get_by_user_id(ctx.author.id)
        
        # Verify team membership
        if not team_member or team_member.team_id != team_obj.team_id:
            await ctx.respond(f"You are not a member of team '{team_obj.name}'.", ephemeral=True)
            return None, None
            
        return team_obj, team_member
    
    @commands.slash_command(name="kick-player", guild_ids=[1370422733086658631])
    @require_verification("user")
    async def kick_player(self, ctx: discord.ApplicationContext, 
                         discord_username: Optional[str] = None, 
                         roblox_username: Optional[str] = None) -> None:
        """
        Kick a player from your team (requires captain or vice-captain role).

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            discord_username (Optional[str]): The Discord username of the player to kick.
            roblox_username (Optional[str]): The Roblox username of the player to kick.
        """
        # Verify team and user permissions
        team_obj, team_member = await self._verify_team_and_team_member(ctx)
        if not team_obj or not team_member:
            return
            
        # Check if user has appropriate role
        if team_member.role not in [RoleType.captain, RoleType.vice_captain]:
            await ctx.respond(f"You must be a captain or vice-captain to kick players.", ephemeral=True)
            return
            
        # Check if at least one username is provided
        if not discord_username and not roblox_username:
            await ctx.respond("Please provide either a Discord username or a Roblox username.", ephemeral=True)
            return
            
        # Find user by discord username if provided
        target_member = None
        if discord_username:
            # Handle both direct mentions and plain usernames
            if discord_username.startswith("<@") and discord_username.endswith(">"):
                user_id = int(discord_username[2:-1])
                try:
                    target_member = await ctx.guild.fetch_member(user_id)
                except:
                    await ctx.respond(f"Could not find user with ID {user_id}.", ephemeral=True)
                    return
            else:
                # Search by username
                members = [m for m in ctx.guild.members if m.name.lower() == discord_username.lower() or 
                          (m.nick and m.nick.lower() == discord_username.lower())]
                if len(members) == 1:
                    target_member = members[0]
                elif len(members) > 1:
                    await ctx.respond(f"Found multiple users with the name '{discord_username}'. Please use a mention instead.", ephemeral=True)
                    return
                else:
                    await ctx.respond(f"Could not find user '{discord_username}'.", ephemeral=True)
                    return
            
            # Get the team member
            target_team_member = self.team_member_repository.get_by_user_id(target_member.id)
            if not target_team_member:
                await ctx.respond(f"{target_member.mention} is not a member of any team.", ephemeral=True)
                return
                
            # Check if the target is on the same team
            if target_team_member.team_id != team_obj.team_id:
                await ctx.respond(f"{target_member.mention} is not a member of your team.", ephemeral=True)
                return
                
            # Cannot kick captain if you're vice-captain
            if target_team_member.role == RoleType.captain and team_member.role == RoleType.vice_captain:
                await ctx.respond(f"Vice-captains cannot kick the team captain.", ephemeral=True)
                return
                
            # Remove from team
            self.team_member_repository.delete(target_team_member.user_id)
            
            # Remove team role
            await target_member.remove_roles(ctx.guild.get_role(team_obj.team_role_id))
            
            await ctx.respond(f"{target_member.mention} has been kicked from team '{team_obj.name}'.")
            return
            
        # Find user by Roblox username if provided
        if roblox_username:
            # Find user by Roblox username in database
            target_user = self.user_repository.get_by_roblox_username(roblox_username)
            if not target_user:
                await ctx.respond(f"Could not find a user with Roblox username '{roblox_username}'.", ephemeral=True)
                return
                
            # Get the team member
            target_team_member = self.team_member_repository.get_by_user_id(target_user.user_id)
            if not target_team_member:
                await ctx.respond(f"User with Roblox username '{roblox_username}' is not a member of any team.", ephemeral=True)
                return
                
            # Check if the target is on the same team
            if target_team_member.team_id != team_obj.team_id:
                await ctx.respond(f"User with Roblox username '{roblox_username}' is not a member of your team.", ephemeral=True)
                return
                
            # Cannot kick captain if you're vice-captain
            if target_team_member.role == RoleType.captain and team_member.role == RoleType.vice_captain:
                await ctx.respond(f"Vice-captains cannot kick the team captain.", ephemeral=True)
                return
                
            # Remove from team
            self.team_member_repository.delete(target_team_member.user_id)
            
            # Try to remove role if user is in the guild
            try:
                target_member = await ctx.guild.fetch_member(target_user.user_id)
                if target_member:
                    await target_member.remove_roles(ctx.guild.get_role(team_obj.team_role_id))
                    await ctx.respond(f"{target_member.mention} has been kicked from team '{team_obj.name}'.")
                else:
                    await ctx.respond(f"User with Roblox username '{roblox_username}' has been kicked from team '{team_obj.name}'.")
            except:
                await ctx.respond(f"User with Roblox username '{roblox_username}' has been kicked from team '{team_obj.name}'.")

    @commands.slash_command(name="invite-player", guild_ids=[1370422733086658631])
    @require_verification("user")
    async def invite_player(self, ctx: discord.ApplicationContext, team_name: str, user: discord.Member) -> None:
        """
        Invite a player to join your team (requires captain or vice-captain role).

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team.
            user (discord.Member): The user to invite.
        """
        # Check if team exists
        team_obj = self.team_repository.get_by_name(team_name)
        if not team_obj:
            await ctx.respond(f"Team '{team_name}' not found.", ephemeral=True)
            return
        
        # Check if inviter is a team captain or vice-captain
        team_member = self.team_member_repository.get_by_user_id(ctx.author.id)
        if not team_member or team_member.team_id != team_obj.team_id or team_member.role not in [RoleType.captain, RoleType.vice_captain]:
            await ctx.respond(f"You must be a captain or vice-captain of team '{team_name}' to invite players.", ephemeral=True)
            return
        
        # Check if user is already in a team
        existing_member = self.team_member_repository.get_by_user_id(user.id)
        if existing_member:
            await ctx.respond(f"{user.mention} is already a member of a team.", ephemeral=True)
            return
        
        # Check if user already has a pending invitation
        pending_invites = self.invitation_repository.get_pending_by_user_id(user.id)
        if pending_invites:
            await ctx.respond(f"{user.mention} already has a pending invitation. They must accept or decline it first.", ephemeral=True)
            return
        
        # Check inviter's pending invitation count
        inviter_id = ctx.author.id
        if inviter_id in self.pending_invites_cache:
            if len(self.pending_invites_cache[inviter_id]) >= self.max_pending_invites:
                await ctx.respond(f"You have reached the maximum limit of {self.max_pending_invites} pending invitations.", ephemeral=True)
                return
        else:
            # Initialize cache for this inviter
            self.pending_invites_cache[inviter_id] = set()
            
            # Refresh cache with current pending invitations from database
            db_pending = self.invitation_repository.get_pending_by_inviter_id(inviter_id)
            for inv in db_pending:
                self.pending_invites_cache[inviter_id].add(inv.invitation_id)
                
            # Check again after refresh
            if len(self.pending_invites_cache[inviter_id]) >= self.max_pending_invites:
                await ctx.respond(f"You have reached the maximum limit of {self.max_pending_invites} pending invitations.", ephemeral=True)
                return
        
        # Acknowledge the interaction immediately to prevent timeout
        await ctx.defer(ephemeral=True)
        
        # Create invitation
        invitation = self.invitation_repository.create(
            team_id=team_obj.team_id,
            user_id=user.id,
            inviter_id=ctx.author.id
        )
        
        # Add to cache
        self.pending_invites_cache[inviter_id].add(invitation.invitation_id)
        
        # Send DM to user
        try:
            embed = discord.Embed(
                title=f"Team Invitation from {team_obj.name}",
                description=f"{ctx.author.mention} has invited you to join their team '{team_obj.name}'.",
                color=discord.Color.blue()
            )
            # Handle expires_at correctly whether it's a string or datetime object
            if isinstance(invitation.expires_at, str):
                expiry_timestamp = int(datetime.datetime.fromisoformat(invitation.expires_at).timestamp())
            else:
                # Already a datetime object
                expiry_timestamp = int(invitation.expires_at.timestamp())
                
            embed.add_field(name="Expires", value=f"<t:{expiry_timestamp}:R>")
            
            # Create view with buttons
            view = PlayerInviteView(
                invitation_data=vars(invitation),
                callback=self._handle_player_response
            )
            
            dm = await user.send(embed=embed, view=view)
            
            # Send admin approval request
            await self._send_admin_approval(ctx.guild, team_obj, user, ctx.author, invitation)
            
            # Use followup instead of respond since we already deferred
            await ctx.followup.send(f"Invitation sent to {user.mention} and admin approval requested.", ephemeral=True)
            
        except discord.Forbidden:
            # Use followup instead of respond since we already deferred
            await ctx.followup.send(f"Unable to send DM to {user.mention}. Make sure they have DMs enabled.", ephemeral=True)
            # Clean up invitation
            self.invitation_repository.update_status(invitation.invitation_id, InvitationStatus.expired)
            self.pending_invites_cache[inviter_id].remove(invitation.invitation_id)
    
    async def _handle_player_response(self, invitation_id: int, status: InvitationStatus, interaction: discord.Interaction) -> None:
        """
        Handle player response to invitation.

        Args:
            invitation_id: The ID of the invitation
            status: The new status of the invitation
            interaction: The interaction that triggered this
        """
        # Update invitation status
        invitation = self.invitation_repository.update_status(invitation_id, status)
        if not invitation:
            return
        
        # Update cache
        if invitation.inviter_id in self.pending_invites_cache:
            if invitation.invitation_id in self.pending_invites_cache[invitation.inviter_id]:
                self.pending_invites_cache[invitation.inviter_id].remove(invitation.invitation_id)
        
        # Handle accepted invitations (they still need admin approval)
        if status == InvitationStatus.accepted:
            # Logic to handle accepted invitation will be handled by admin approval
            pass
        elif status == InvitationStatus.declined:
            # Notify team captain
            guild = self.bot.get_guild(1370422733086658631)  # Your guild ID
            if guild:
                inviter = guild.get_member(invitation.inviter_id)
                if inviter:
                    team = self.team_repository.get_by_id(invitation.team_id)
                    user = guild.get_member(invitation.user_id)
                    user_mention = user.mention if user else f"User (ID: {invitation.user_id})"
                    team_name = team.name if team else f"Team (ID: {invitation.team_id})"
                    
                    try:
                        await inviter.send(f"{user_mention} has declined your invitation to join '{team_name}'")
                    except discord.Forbidden:
                        pass  # Can't send DM, but that's okay
    
    async def _send_admin_approval(self, guild: discord.Guild, team: Team, user: discord.Member, inviter: discord.Member, invitation) -> None:
        """
        Send invitation approval request to the admin approval channel.

        Args:
            guild: The Discord guild
            team: The team object
            user: The invited user
            inviter: The user who sent the invitation
            invitation: The invitation object
        """
        # Get approval channel from config
        config = self.server_config_repository.get_by_guild_id(guild.id)
        if not config or not config.team_invite_approval_channel_id:
            # Try to inform the inviter that no approval channel is set
            try:
                await inviter.send(f"No team invitation approval channel has been set up. Please ask an admin to set one using `/register-approval-channel`")
            except discord.Forbidden:
                pass
            return
        
        # Get the approval channel
        approval_channel = guild.get_channel(config.team_invite_approval_channel_id)
        if not approval_channel:
            return
        
        # Create an embed for the approval
        embed = discord.Embed(
            title="Team Invitation Approval Request",
            description=f"{inviter.mention} wants to invite {user.mention} to join team '{team.name}'.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Team", value=team.name, inline=True)
        embed.add_field(name="Invited Player", value=user.mention, inline=True)
        embed.add_field(name="Invited By", value=inviter.mention, inline=True)
        # Handle expires_at correctly whether it's a string or datetime object
        if isinstance(invitation.expires_at, str):
            expiry_timestamp = int(datetime.datetime.fromisoformat(invitation.expires_at).timestamp())
        else:
            # Already a datetime object
            expiry_timestamp = int(invitation.expires_at.timestamp())
            
        embed.add_field(name="Expires", value=f"<t:{expiry_timestamp}:R>", inline=True)
        
        # Create view with approval buttons
        view = AdminApprovalView(
            invitation_data=vars(invitation),
            callback=self._handle_admin_response
        )
        
        # Send to approval channel
        await approval_channel.send(embed=embed, view=view)
    
    async def _handle_admin_response(self, invitation_id: int, approved: bool, interaction: discord.Interaction, reason: str = None) -> None:
        """
        Handle admin response to invitation approval request.

        Args:
            invitation_id: The ID of the invitation
            approved: Whether the invitation was approved
            interaction: The interaction that triggered this
            reason: The reason for rejection (if not approved)
        """
        
        # Get invitation details
        try:
            invitation = self.invitation_repository.get_by_id(invitation_id)
            if not invitation:
                await interaction.edit_original_response(content="This invitation no longer exists.")
                return
                
            # Update cache if needed
            if invitation.inviter_id in self.pending_invites_cache and invitation.invitation_id in self.pending_invites_cache[invitation.inviter_id]:
                self.pending_invites_cache[invitation.inviter_id].remove(invitation.invitation_id)
            
            # Get relevant objects using DTO pattern
            guild = interaction.guild
            team_dto = self.team_repository.get_by_id(invitation.team_id)  # This returns a TeamDTO
            user = guild.get_member(invitation.user_id)
            inviter = guild.get_member(invitation.inviter_id)
            
            # Verify all objects were found successfully
            if not team_dto:
                await interaction.edit_original_response(content=f"Could not find team (ID: {invitation.team_id}).")
                return
                
        except Exception as e:
            await interaction.edit_original_response(content=f"Error processing invitation: {str(e)}")
            return
        
        if not team_dto or not user or not inviter:
            await interaction.edit_original_response(content="Could not find team or user information.")
            return
        
        if approved:
            # Check if invitation was accepted by the player
            if invitation.status != InvitationStatus.accepted:
                await interaction.edit_original_response(content=f"The invitation has not been accepted by the player yet.")
                return
                
            # Add user to team
            self.team_member_repository.create(
                team_id=team_dto.team_id,
                user_id=user.id,
                role=RoleType.member,
                team_display_name=user.display_name
            )
            
            # Assign team role to user
            team_role = guild.get_role(team_dto.team_role_id)
            if team_role:
                try:
                    await user.add_roles(team_role, reason=f"Joined team {team_dto.name}")
                except discord.Forbidden:
                    await interaction.edit_original_response(content="Could not assign team role due to missing permissions.")
            
            # Notify user and team captain
            try:
                await user.send(f"Your request to join team '{team_dto.name}' has been approved by the admins!")
            except discord.Forbidden:
                pass
                
            try:
                await inviter.send(f"{user.mention} has been added to your team '{team_dto.name}'!")
            except discord.Forbidden:
                pass
                
            # Edit the approval message to show it was approved
            if interaction.message:
                embed = interaction.message.embeds[0]
                embed.color = discord.Color.green()
                embed.title = "Team Invitation Approved"
                await interaction.message.edit(embed=embed, view=None)
                
            # Update the original response with success message
            await interaction.edit_original_response(content=f"Successfully approved {user.display_name} to join team '{team_dto.name}'!")
                
        else:  # Rejected
            # Update invitation status
            self.invitation_repository.update_status(invitation.invitation_id, InvitationStatus.declined)
            
            # Notify user and team captain
            rejection_msg = f"Your invitation to join team '{team_dto.name}' was not approved by the admins."
            if reason:
                rejection_msg += f" Reason: {reason}"
                
            try:
                await user.send(rejection_msg)
            except discord.Forbidden:
                pass
                
            try:
                await inviter.send(f"Your invitation for {user.mention} to join team '{team.name}' was not approved by the admins." + (f" Reason: {reason}" if reason else ""))
            except discord.Forbidden:
                pass
                
            # Edit the approval message to show it was rejected
            if interaction.message:
                embed = interaction.message.embeds[0]
                embed.color = discord.Color.red()
                embed.title = "Team Invitation Rejected"
                if reason:
                    embed.add_field(name="Reason", value=reason)
                await interaction.message.edit(embed=embed, view=None)

    def _format_rating_stars(self, rating: int) -> str:
        """Format a numeric rating as unicode stars"""
        if rating is None:
            return ""
        
        # Convert from DB format (0-10) to display format (0-5 with half stars)
        stars = rating / 2  # Convert back to 0-5 scale
        
        # Build the star string
        full_stars = int(stars)
        has_half_star = (stars - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if has_half_star else 0)
        
        star_str = "★" * full_stars
        if has_half_star:
            star_str += "⯪"
        star_str += "☆" * empty_stars
        
        return star_str

# Add the required setup function
def setup(bot: commands.Bot):
    bot.add_cog(TeamCommands(bot))
