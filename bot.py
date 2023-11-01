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
    channel = after.channel or before.channel  # Get the channel, either the joined or the left one
    if not channel:  # If no channel is associated, do nothing
        return

    if before.channel is None and after.channel is not None:  # User joined a voice channel
        vc = discord.utils.get(bot.voice_clients, guild=member.guild)  # Get the current voice client, if any
        if not vc:  # If bot is not already in a voice channel
            vc = await channel.connect()  # Join the voice channel if not already connected
        
        while not vc.is_connected():
            await asyncio.sleep(0.1)  # Wait for the voice client to connect
        
        vc.stop()  # Stop any currently playing audio
        await asyncio.sleep(1) # Half second delay before talking
        vc.play(discord.FFmpegPCMAudio('sounds/greeting.mp3'), after=lambda e: print('done', e))

    elif before.channel is not None and after.channel is None:  # User left a voice channel
        if len(before.channel.members) == 1:  # If the bot is the only member left in the channel
            vc = discord.utils.get(bot.voice_clients, guild=member.guild)  # Get the current voice client, if any
            if vc:
                await vc.disconnect()  # Disconnect from the voice channel

bot.run(DISCORD_TOKEN)