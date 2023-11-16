import discord
from discord.ext import commands, tasks
import os

from db.db import setup_db_connection
from cogs.text_commands import TextCommands
from cogs.voice_events import VoiceEvents
from cogs.steam_commands import SteamCommands
from cogs.settings import Settings
from cogs.music import Music

import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='*', intents=discord.Intents.all())
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("No DISCORD_TOKEN found in environment variables")


# Local Development
if os.getenv('LOCAL_ENV') == 'true':
    if not discord.opus.is_loaded():
        discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.4/lib/libopus.dylib')


# Add local version with no await
@bot.event
async def on_ready():
    print("KT is online")
    
    # Boot up the database connection
    session = setup_db_connection()
    
    # Initiate cog objects
    await bot.add_cog(TextCommands(bot))
    await bot.add_cog(SteamCommands(bot, session))
    await bot.add_cog(VoiceEvents(bot, session))
    await bot.add_cog(Settings(bot, bot.get_cog("VoiceEvents"), session))
    await bot.add_cog(Music(bot))


bot.run(DISCORD_TOKEN)