import discord
from discord.ext import commands
import os
import asyncio

from db.db import setup_db_connection
from cogs.text_commands import TextCommands
from cogs.voice_events import VoiceEvents
from cogs.steam_commands import SteamCommands
from cogs.settings import Settings
from cogs.music import Music
from cogs.xp_system import XpSystem
from cogs.poke_quiz import PokeQuiz
from cogs.ai import AI
from initializers.axiom_setup import AxiomHelper
from initializers.tracing_setup import tracer
from jobs.cache_event_handler import BatchCacheEventHandler

axiom = AxiomHelper()

import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='*', intents=discord.Intents.all())
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

cache_event_handler = BatchCacheEventHandler()

# Local Development
if os.getenv('LOCAL_ENV') == 'true':
    if not discord.opus.is_loaded():
        discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.4/lib/libopus.dylib')

@bot.event
async def on_ready():
    with tracer.start_as_current_span("initial_boot_time", {"type": "boot_time"}):
        # Boot up the database connection
        session = setup_db_connection()
        
        # Initiate cog objects
        await bot.add_cog(TextCommands(bot))
        await bot.add_cog(SteamCommands(bot, session, cache_event_handler))
        await bot.add_cog(VoiceEvents(bot, session, cache_event_handler))
        await bot.add_cog(Settings(bot, bot.get_cog("VoiceEvents"), session))
        await bot.add_cog(Music(bot))
        await bot.add_cog(XpSystem(bot, session))
        await bot.add_cog(PokeQuiz(bot, session, cache_event_handler))
        await bot.add_cog(AI(bot))
        await bot.tree.sync()

        # Start the cache event handler
        asyncio.create_task(cache_event_handler.aggregation_scheduler())
        
        print("KT is online")


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

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

bot.run(DISCORD_TOKEN)