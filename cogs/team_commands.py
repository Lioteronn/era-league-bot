import discord
from discord.ext import commands
from cogs.permissions.admin_checker import is_admin
from database.models.team import Team
from database.repository.team_repository import TeamRepository
from database.repository.team_member_repository import TeamMemberRepository
from images.image_downloader import download_and_save_image
from database.models.team_member import RoleType
from typing import Union


class TeamCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.team_repository = TeamRepository()
        self.team_member_repository = TeamMemberRepository()

    @commands.slash_command(name="create-team", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    async def create_team(self, ctx: discord.ApplicationContext, team_name: str, hexcode: str = None, logo_url: str = None) -> None:
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

        logo_path = download_and_save_image(logo_url, team_name)

        team_obj = await self.team_repository.create(create_role_func=self.create_role,
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
    async def set_captain(self, ctx: discord.ApplicationContext, team_name: str, user: str) -> None:
        """
        Set the captain for the team.

        Args:
            ctx (discord.ApplicationContext): The context of the command.
            team_name (str): The name of the team.
            user (discord.Member): The user to set as the captain.
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
        
        if team_member.role == RoleType.captain:
            await ctx.respond(f"User {user.mention} is already the captain of team '{team_name}'.")
            return
        
        self.team_repository.update(team_id=team_obj.team_id, team_captain_id=team_member.user_id)
        self.team_member_repository.update(team_id=team_obj.team_id, user_id=team_member.user_id, role=RoleType.captain)
        await ctx.respond(f"Captain for team '{team_obj.name}' set to {user.mention}.")
        
    @commands.slash_command(name="search-team", guild_ids=[1370422733086658631])
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

        embed = discord.Embed(
            title=team_title,
            description=f"",
            color=discord.Color(int(team_obj.hexcode[1:], 16))
        )
        embed.set_thumbnail(url="attachment://logo.png")
        embed.add_field(name="🔹 Current Roster", value="- No players added yet.", inline=True)
        embed.add_field(name="🔹 Team Role", value=f"<@&{team_role.id}>", inline=True)
        await ctx.respond(embed=embed, files=[file])

    async def create_role(self, ctx: discord.ApplicationContext, team_obj: Team) -> int:
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

    @commands.slash_command(name="force-add-player-to-team", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
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
        await ctx.respond(f"User {user.mention} added to team '{team_obj.name}'.")

# Add the required setup function
def setup(bot: commands.Bot):
    """Setup function for Discord.py to load the cog."""
    bot.add_cog(TeamCommands(bot))
