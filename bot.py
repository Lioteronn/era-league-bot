from discord import guild
from discord.ext import commands
from intents import get_intents
from config import BOT_TOKEN
from database.db import init_db
from cogs.cogs_loader import load_cogs


bot = commands.Bot(
    command_prefix='!',
    intents=get_intents()
)
load_cogs(bot)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')
    init_db()
    try:
        guild_id = 1370422733086658631  # Your guild ID
        await bot.sync_commands()
        print(f"Synced commands for guild ID: {guild_id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")


bot.run(BOT_TOKEN)
