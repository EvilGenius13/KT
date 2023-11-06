import discord
from discord.ext import commands, tasks
import datetime
import pytz
import random
import asyncio


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.greeting_state = True
        self.checkin_state = False
        self.recurring_state = False
        self.intro_greetings = [
            "sounds/hey.mp3",
            "sounds/howdy.mp3",
            "sounds/welcome.mp3",
            "sounds/whatsup.mp3",
        ]
        self.schedule_break.start()  # Start the looping tasks
        self.break_time.start()

    def cog_unload(self):
        self.schedule_break.cancel()  # Cancel the looping task when the cog is unloaded
        self.break_time.cancel()

    @tasks.loop(minutes=1)  # Check the time every minute
    async def schedule_break(self):
        current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))

        # TODO: This is for testing purposes only. Remove when ready to deploy
        # if current_time.minute % 5 == 0:  # If the current minute is a multiple of 5 **FOR TESTING PURPOSES**
        if current_time.hour == 21 and current_time.minute == 0:  # If it's 9 PM EST
            for guild in self.bot.guilds:  # Check all guilds the bot is connected to
                vc = discord.utils.get(self.bot.voice_clients, guild=guild)
                if (
                    vc and vc.is_connected()
                ):  # If the bot is connected to a voice channel in this guild
                    vc.stop()  # Stop any currently playing audio
                    await asyncio.sleep(
                        0.5
                    )  # Optional: wait for half a second before playing the new audio
                    vc.play(
                        discord.FFmpegPCMAudio("sounds/checkin.mp3"),
                        after=lambda e: print("done", e),
                    )

    @tasks.loop(minutes=1)  # Check the time every minute
    async def break_time(self):
        current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))

        if current_time.minute == 0 and current_time.hour % 2 == 0:
            for guild in self.bot.guilds:
                vc = discord.utils.get(self.bot.voice_clients, guild=guild)
                if vc and vc.is_connected():
                    vc.stop()
                    await asyncio.sleep(0.5)
                    vc.play(
                        discord.FFmpegPCMAudio("sounds/checkin2.mp3"),
                        after=lambda e: print("done", e),
                    )



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.greeting_state == False:
            return
        channel = (
            after.channel or before.channel
        )  # Get the channel, either the joined or the left one
        if not channel:  # If no channel is associated, do nothing
            return

        if (
            before.channel is None and after.channel is not None
        ):  # User joined a voice channel
            vc = discord.utils.get(
                self.bot.voice_clients, guild=member.guild
            )  # Get the current voice client, if any
            if not vc:  # If bot is not already in a voice channel
                vc = (
                    await channel.connect()
                )  # Join the voice channel if not already connected

            while not vc.is_connected():
                await asyncio.sleep(0.5)  # Wait for the voice client to connect

            await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"Everyone play in {channel.name}"
            )
        )

            vc.stop()  # Stop any currently playing audio
            await asyncio.sleep(1)  # One second delay before talking
            random_intro = random.choice(self.intro_greetings)
            vc.play(
                discord.FFmpegPCMAudio(random_intro), after=lambda e: print("done", e)
            )

        elif (
            before.channel is not None and after.channel is None
        ):  # User left a voice channel
            if (
                len(before.channel.members) == 1
            ):  # If the bot is the only member left in the channel
                vc = discord.utils.get(
                    self.bot.voice_clients, guild=member.guild
                )  # Get the current voice client, if any
                if vc:
                    await vc.disconnect()  # Disconnect from the voice channel
                    await self.bot.change_presence(activity=None)
