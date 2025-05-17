from discord import guild
from discord.ext import commands
from intents import get_intents
from config import BOT_TOKEN
from database.db import init_db
import asyncio
import os

# Define bot with intents
bot = commands.Bot(
    command_prefix='!',
    intents=get_intents()
)

# Load cogs in the on_ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')
    init_db()
    
    # Load all cogs manually without await expressions
    cog_files = ['team_commands', 'verification_commands', 'scrim_commands']
    for cog in cog_files:
        try:
            # Use load_extension directly, not async
            bot.load_extension(f'cogs.{cog}')
            print(f'Successfully loaded extension {cog}')
        except Exception as e:
            print(f'Failed to load cog {cog}: {str(e)}')
    
    try:
        # Sync commands globally - this is a Pycord 2.x compatible method
        print("Syncing commands globally...")
        guild_id = 1062306579636047892  # Your guild ID
        # For Pycord, we can just use the sync_commands method
        await bot.sync_commands()
        print(f"Synced commands globally")
    except Exception as e:
        print(f"Error syncing commands: {e}")


bot.run(BOT_TOKEN)
