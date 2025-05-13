import discord
from discord.ext import commands
from database.repository.user_repository import UserRepository
from utils.bloxlink import BloxlinkAPI
from utils.verification import require_verification, ensure_user_verified
from cogs.permissions.admin_checker import is_admin


class VerificationCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_repository = UserRepository()
    
    @commands.slash_command(name="verify", guild_ids=[1370422733086658631])
    async def verify(self, ctx: discord.ApplicationContext):
        """
        Verify your Roblox account using Bloxlink.
        """
        # This command directly checks the verification status and creates/updates the user
        verified = await ensure_user_verified(ctx)
        
        if verified:
            await ctx.respond("Your account is verified with Bloxlink and has been registered in our system.", ephemeral=True)
        # If not verified, ensure_user_verified already sent an error message
    
    @commands.slash_command(name="verification-status", guild_ids=[1370422733086658631])
    async def verification_status(self, ctx: discord.ApplicationContext, user: discord.Member = None):
        """
        Check the verification status of a user.

        Args:
            user (discord.Member, optional): The user to check. Defaults to the command author.
        """
        target = user or ctx.author
        
        # Check if the user exists in the database
        db_user = self.user_repository.get_by_id(target.id)
        
        if not db_user:
            await ctx.respond(f"{target.mention} is not registered in our system. Use `/verify` to register.", ephemeral=True)
            return
        
        if not db_user.is_roblox_verified:
            await ctx.respond(f"{target.mention} is registered but not verified with Bloxlink. Please use the `/verify` command.", ephemeral=True)
            return
        
        # User is verified
        embed = discord.Embed(
            title="Verification Status",
            description=f"{target.mention} is verified with Bloxlink.",
            color=discord.Color.green()
        )
        embed.add_field(name="Discord Username", value=target.name, inline=True)
        embed.add_field(name="Roblox Username", value=db_user.roblox_username, inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    @commands.slash_command(name="force-verify", guild_ids=[1370422733086658631])
    @commands.check(is_admin)
    @require_verification()
    async def force_verify(self, ctx: discord.ApplicationContext, user: discord.Member, roblox_username: str):
        """
        Force verify a user (admin only).

        Args:
            user (discord.Member): The user to verify.
            roblox_username (str): The Roblox username to associate with the user.
        """
        # Check if user already exists
        db_user = self.user_repository.get_by_id(user.id)
        
        if db_user:
            # Update existing user
            self.user_repository.update_roblox_verification(
                user_id=user.id,
                is_verified=True,
                roblox_username=roblox_username
            )
        else:
            # Create new user
            self.user_repository.create(
                user_id=user.id,
                username=user.name,
                display_name=user.display_name,
                is_roblox_verified=True,
                roblox_username=roblox_username
            )
        
        await ctx.respond(f"{user.mention} has been force verified with Roblox username '{roblox_username}'.", ephemeral=True)


# Add the required setup function
def setup(bot: commands.Bot):
    bot.add_cog(VerificationCommands(bot))
