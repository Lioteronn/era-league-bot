import discord
from typing import Optional, Dict, Any, Callable, Awaitable
from database.repository.user_repository import UserRepository
from utils.bloxlink import BloxlinkAPI
import functools
import logging

logger = logging.getLogger(__name__)

user_repository = UserRepository()

async def ensure_user_verified(ctx: discord.ApplicationContext, target_user: discord.Member = None) -> bool:
    """
    Ensure that a user is verified through Bloxlink and exists in the database.
    If the user exists in the database but isn't marked as verified, it will check with Bloxlink.
    If the user doesn't exist in the database, it will check with Bloxlink and create an entry.
    
    Args:
        ctx: The command context
        target_user: The user to check (defaults to the command author if not provided)
        
    Returns:
        True if the user is verified, False otherwise
    """
    user = target_user or ctx.author
    guild = ctx.guild
    
    # Check if user exists in database
    db_user = user_repository.get_by_id(user.id)
    
    # If user already exists and is verified, we're good
    if db_user and db_user.is_roblox_verified:
        return True
        
    # Either user doesn't exist or isn't marked as verified, check with Bloxlink
    verified, bloxlink_data = await BloxlinkAPI.get_roblox_user(guild.id, user.id)
    
    if not verified:
        # User is not verified with Bloxlink
        error_message = f"{user.mention} is not verified with Bloxlink. Please verify with Bloxlink first by using the `/verify` command."
        await ctx.respond(error_message, ephemeral=True)
        return False
    
    # User is verified with Bloxlink, extract Roblox ID (free version) or username (premium)
    try:
        roblox_id = bloxlink_data.get('robloxID')
        roblox_username = bloxlink_data.get('robloxUsername', f'RobloxUser_{roblox_id}')
        
        if not roblox_id:
            logger.error(f"Bloxlink data missing Roblox ID: {bloxlink_data}")
            await ctx.respond(f"Could not retrieve Roblox ID for {user.mention} from Bloxlink. Please contact an administrator.", ephemeral=True)
            return False
            
        # Update or create user in database
        if db_user:
            user_repository.update_roblox_verification(
                user_id=user.id,
                is_verified=True,
                roblox_username=roblox_username
            )
        else:
            user_repository.create(
                user_id=user.id,
                username=user.name,
                display_name=user.display_name,
                is_roblox_verified=True,
                roblox_username=roblox_username
            )
            
        return True
        
    except Exception as e:
        logger.error(f"Error updating user verification status: {str(e)}")
        await ctx.respond(f"An error occurred while updating verification status for {user.mention}. Please try again later.", ephemeral=True)
        return False

def require_verification(target_param: str = None):
    """
    Decorator to require Bloxlink verification for a command.
    
    Args:
        target_param: The name of the parameter that contains the target user to check
                      If None, only the command author will be checked
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx: discord.ApplicationContext, *args, **kwargs):
            # Check command author first
            if not await ensure_user_verified(ctx):
                return
                
            # Check target user if specified
            if target_param and target_param in kwargs:
                target_user = kwargs[target_param]
                if isinstance(target_user, discord.Member) and not await ensure_user_verified(ctx, target_user):
                    return
                    
            # All verifications passed, run the original command
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator
