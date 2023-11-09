import discord
from discord.ext import commands, tasks
import datetime
import pytz
import random
import asyncio


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._voice_state_lock = asyncio.Lock()
        self.intro_greetings = [
            "sounds/hey.mp3",
            "sounds/howdy.mp3",
            "sounds/welcome.mp3",
            "sounds/whatsup.mp3",
        ]
        #Setting up states
        self.greeting_state = True
        self.checkin_state = False
        self.recurring_state = False
        self._current_hours = 0
        self._current_minutes = 0
        
        # Start the looping tasks
        self.schedule_break.start()  # Start the looping tasks
        self.break_time.start()

    @property
    def current_hours(self):
        return self._current_hours

    @current_hours.setter
    def current_hours(self, value):
        if 0 <= value < 24:
            self._current_hours = value
        else:
            raise ValueError("Hours must be between 0 and 23")
    
    @property
    def current_minutes(self):
        return self._current_minutes
    
    @current_minutes.setter
    def current_minutes(self, value):
        if 0 <= value < 60:
            self._current_minutes = value
        else:
            raise ValueError("Minutes must be between 0 and 59")

    def cog_unload(self):
        self.schedule_break.cancel()  # Cancel the looping task when the cog is unloaded
        self.break_time.cancel()

    @tasks.loop(minutes=1)  # Check the time every minute
    async def schedule_break(self):
        if not self.checkin_state:
            return
        
        current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))

        if current_time.hour == self.current_hours and current_time.minute == self.current_minutes:
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
        if not self.recurring_state:
            return
        
        current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))
        
        # if current_time.minute % 5 == 0:  # If the current minute is a multiple of 5 **FOR TESTING PURPOSES**
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
        if not self.greeting_state:
            return

        async with self._voice_state_lock:  # Lock to ensure consistency
            # User joined a voice channel
            if before.channel is None and after.channel is not None:
                vc = discord.utils.get(self.bot.voice_clients, guild=member.guild)
                if not vc:
                    # Bot is not in a channel, so join the user's channel
                    vc = await after.channel.connect()

                # Check if bot is already playing audio
                if not vc.is_playing():
                    # Bot is not playing audio, so play a greeting
                    random_intro = random.choice(self.intro_greetings)
                    vc.play(
                        discord.FFmpegPCMAudio(random_intro),
                        after=lambda e: print("done", e),
                    )
                else:
                    # Bot is already playing audio. Decide if you want to queue here.
                    print(f"Skipped greeting for {member} as audio is already playing.")

            # User switched from one channel to another
            elif before.channel is not None and after.channel is not None and before.channel != after.channel:
                # Handle channel switch if necessary
                pass

            # User left a voice channel
            elif before.channel is not None and after.channel is None:
                # Check if bot is the only one left
                if len(before.channel.members) == 1:
                    # Bot is alone in the voice channel, disconnect
                    vc = discord.utils.get(self.bot.voice_clients, guild=member.guild)
                    if vc:
                        await vc.disconnect()
                        await self.bot.change_presence(activity=None)
            else:
                # This is likely a mute/unmute or deafen/undeafen event, do nothing
                pass

