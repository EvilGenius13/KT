import discord
from discord.ext import commands, tasks
import os
import asyncio
import datetime
import pytz
import random

from cogs.text_commands import TextCommands
from cogs.voice_events import VoiceEvents

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
    await bot.add_cog(VoiceEvents(bot))
    # play_sound_at_9pm.start()  # Start the looping task

bot.run(DISCORD_TOKEN)