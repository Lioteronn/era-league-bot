import discord
from discord.ext import commands


NO_PERMS_MESSAGE = "You don't have permissions to run this command."


async def is_admin(ctx: discord.ApplicationContext):
    """
    Check if the user has admin permissions.
    
    Args:
        ctx (commands.Context): The context of the command.
        
    Returns:
        bool: True if the user has administrator permissions, False otherwise.
    """
    # Check if user has administrator permissions
    if ctx.author.guild_permissions.administrator:
        return True
        
    # Check if the user has a role named "Admin" or "Administrator"
    admin_role_names = ["Admin", "Administrator"]
    user_roles = [role.name for role in ctx.author.roles]
    if any(role in user_roles for role in admin_role_names):
        return True
        
    # If all checks fail, inform the user and return False
    await ctx.respond(NO_PERMS_MESSAGE, ephemeral=True)
    return False


async def is_captain(ctx: discord.ApplicationContext):
    if ctx.author.guild_permissions.administrator:
        return True
    
    role_names = [role.name for role in ctx.author.roles]
    if 'Captain' in role_names:
        return True
    
    await ctx.respond(NO_PERMS_MESSAGE, ephemeral=True)
    return False
    