import discord
import os
from discord.ext import commands
import asyncio

from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='*', intents=discord.Intents.all())

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:  # User joined a voice channel
        channel = after.channel  # The channel the user joined
        if not discord.utils.get(bot.voice_clients, guild=member.guild):  # Check if bot is not already in a voice channel
            vc = await channel.connect()  # Join the voice channel
            vc.play(discord.FFmpegPCMAudio('sounds/greeting.mp3'), after=lambda e: print('done', e))
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()  # Disconnect from the voice channel after audio is done playing


bot.run(DISCORD_TOKEN)