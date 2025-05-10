import os
import discord
from discord.ext import commands

# List of cogs to load
COGS = [
    'team_commands',
    # Add other cog names here
]

def load_cogs(bot: commands.Bot):
    """Load all cogs in the COGS list."""
    for cog in COGS:
        try:
            bot.load_extension(f'cogs.{cog}')
            print(f'Successfully loaded extension {cog}')
        except Exception as e:
            print(f'Failed to load cog {cog}: {str(e)}')
            
# Required setup function for Discord.py extension loading
def setup(bot: commands.Bot):
    """Setup function for discord.py extension loading."""
    # This might seem redundant, but it's needed when cogs_loader is loaded as an extension itself
    pass
