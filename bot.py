import discord
from discord.ext import commands, tasks
import os
import time
import json
from telemetry.axiom_setup import AxiomHelper

from db.db import setup_db_connection
from cogs.text_commands import TextCommands
from cogs.voice_events import VoiceEvents
from cogs.steam_commands import SteamCommands
from cogs.settings import Settings
from cogs.music import Music
from telemetry.tracing_setup import tracer

axiom = AxiomHelper()

import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='*', intents=discord.Intents.all())
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

# Bot Start Timing
start_time = time.time()

# Local Development
if os.getenv('LOCAL_ENV') == 'true':
    if not discord.opus.is_loaded():
        discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.4/lib/libopus.dylib')


# Add local version with no await
@bot.event
async def on_ready():
    # Boot up the database connection
    session = setup_db_connection()
    
    # Initiate cog objects
    await bot.add_cog(TextCommands(bot))
    await bot.add_cog(SteamCommands(bot, session))
    await bot.add_cog(VoiceEvents(bot, session))
    await bot.add_cog(Settings(bot, bot.get_cog("VoiceEvents"), session))
    await bot.add_cog(Music(bot))

    end_time = time.time()
    boot_time = end_time - start_time

    data = [{"type": "boot_time", "value": boot_time}]
    axiom.send_event(data)
    
    print("KT is online")
    # with tracer.start_as_current_span("foo"):
    #     print("Axiom, tracing!")


@bot.event
async def on_command_error(ctx, error):
    # Prepare the error data
    error_data = [{
        "type": "error",
        "description": str(error),
        "command": ctx.command.name if ctx.command else "None",
        "guild_id": str(ctx.guild.id) if ctx.guild else "DM",
        "user_id": str(ctx.author.id)
    }]

    # Send the error data to Axiom
    axiom.send_event(error_data)

    await ctx.send(f"An error occurred: {str(error)}")

bot.run(DISCORD_TOKEN)