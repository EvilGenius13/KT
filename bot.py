import discord
from discord.ext import commands, tasks
import os

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

# TODO: Remove Eventually when local testing is no longer neededLocal Env Only
if not discord.opus.is_loaded():
    discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.4/lib/libopus.dylib')

@bot.event
async def on_ready():
    print("KT is online")
    await bot.add_cog(TextCommands(bot))
    await bot.add_cog(SteamCommands(bot))
    await bot.add_cog(VoiceEvents(bot))
    await bot.add_cog(Settings(bot, bot.get_cog("VoiceEvents")))
    await bot.add_cog(Music(bot))

bot.run(DISCORD_TOKEN)