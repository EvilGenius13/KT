import discord
from discord.ext import commands, tasks
import datetime
import pytz
import random
import os
import asyncio
import json
from db.db import get_guild_settings
from google.cloud import texttospeech
import uuid
from initializers.tracing_setup import tracer
from helpers.starfire import Starfire
from initializers.redis import r
import os

# Experimental settings
from pyht import Client, TTSOptions, Format
from dotenv import load_dotenv
load_dotenv()
client = Client(
    user_id=os.getenv("HT_USER_ID"),
    api_key=os.getenv("HT_KEY")
)

class VoiceEvents(commands.Cog):
    def __init__(self, bot, session, cache_event_handler):
        self.bot = bot
        self._voice_state_lock = asyncio.Lock()
        self.session = session
        self.cache_event_handler = cache_event_handler
        self.greetings = [
            "Hey {username}, great to see you here!",
            "Hello {username}, welcome to the channel!",
            "Greetings, {username}! Hope you're doing well today.",
            "Hi there, {username}! Ready for some fun?",
            "{username}, you've joined us! Fantastic to have you here.",
            "Welcome aboard, {username}! Let's make this a great day.",
            "Good to see you, {username}! We've been expecting you.",
            "Ah, {username}, you've arrived! Let the adventure begin.",
            "Hello {username}, thrilled to have you join us today!",
            "Hi {username}, welcome! Looking forward to chatting with you."
        ]
        self.break_messages = [
            "Hey everyone, KT here. Time to get up, stretch your legs, and maybe grab a snack!",
            "Hello all, this is KT reminding you to take a short break. A quick walk or some fresh air can be really refreshing.",
            "Hi everyone, it's KT! Don't forget to rest your eyes, move around a bit, and stay hydrated."
        ]
        self.scheduled_break_messages = [
            "Attention everyone, it's time for our scheduled break. Let's take a moment to step away, relax, and recharge. We'll be back in action soon!"
        ]
        
        # Start the looping tasks
        self.schedule_break.start()  # Start the looping tasks
        self.break_time.start()

    def cog_unload(self):
        self.schedule_break.cancel()  # Cancel the looping task when the cog is unloaded
        self.break_time.cancel()

    async def get_cached_guild_settings(self, guild_id):
        redis_key = f"guild_settings:{guild_id}"
        cached_settings = r.get(redis_key)

        if cached_settings is not None:
            self.cache_event_handler.increment_cache_hit()
            return json.loads(cached_settings)
        else:
            settings = await get_guild_settings(self.session, guild_id)
            if settings:
                r.set(redis_key, json.dumps(settings))
                self.cache_event_handler.increment_cache_miss()
                return settings
            return None

    async def play_greeting(self, voice_client, text):
        with tracer.start_as_current_span("play_greeting"):
            with tracer.start_as_current_span("initialize_tts_client"):
                # Initialize the Text-to-Speech client
                tts_client = texttospeech.TextToSpeechClient()

                # Set the text input to be synthesized
                synthesis_input = texttospeech.SynthesisInput(text=text)

                # Build the voice request, select the language code and the SSML voice gender
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Studio-O",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )

                # Select the type of audio file you want returned
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    pitch= 2.0,
                    speaking_rate= 1.0
                )
            with tracer.start_as_current_span("synthesize_speech"):
                # Perform the text-to-speech request
                response = tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                # Save the response to an MP3 file
                tts_filename = f"sounds/tts-{uuid.uuid4()}.mp3"
                os.makedirs(os.path.dirname(tts_filename), exist_ok=True)
                
                with open(tts_filename, "wb") as out:
                    out.write(response.audio_content)

                # Define an 'after' callback function to delete the file
                def after_playing(error):
                    print("TTS playback finished:", error)
                    try:
                        os.remove(tts_filename)  # Delete the file
                    except OSError as e:
                        print(f"Error deleting file {tts_filename}: {e}")

            with tracer.start_as_current_span("play_audio"):
                # Play the generated MP3 file in the voice channel
                voice_client.play(
                    discord.FFmpegPCMAudio(tts_filename),
                    after=after_playing
                )

    async def play_greeting_experimental(self, voice_client, text):
        with tracer.start_as_current_span("play_greeting_experimental"):
            try:
                # Set up TTS options
                options = TTSOptions(
                    voice="s3://voice-cloning-zero-shot/d585a4ac-7cf6-4f68-b119-115fa52d6ad1/enhanced/manifest.json",
                    sample_rate=44_100,
                    format=Format.FORMAT_MP3,
                    speed=1,
                    temperature=2,
                    text_guidance=1,
                    voice_guidance=2,
                )

                # Generate speech and save to a file
                tts_filename = f"sounds/tts-experimental-{uuid.uuid4()}.mp3"
                os.makedirs(os.path.dirname(tts_filename), exist_ok=True)
                with open(tts_filename, "wb") as out_file:
                    for audio_chunk in client.tts(text=text, options=options):
                        out_file.write(audio_chunk)  # Write each chunk to the file

                # Define an 'after' callback function to delete the file
                def after_playing(error):
                    print("Play.ht TTS playback finished:", error)
                    try:
                        os.remove(tts_filename)  # Delete the file after playing
                    except OSError as e:
                        print(f"Error deleting file {tts_filename}: {e}")

                # Play the generated MP3 file in the voice channel
                with tracer.start_as_current_span("play_audio"):
                    voice_client.play(
                        discord.FFmpegPCMAudio(tts_filename),
                        after=after_playing
                    )

            except Exception as e:
                error_data = {
                    "type": "error",
                    "description": str(e),
                }
                Starfire.log(error_data)
                print("Failed to play greeting:", e)
        
    @tasks.loop(minutes=1)  # Check the time every minute
    async def schedule_break(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            settings = await self.get_cached_guild_settings(guild_id)

            if settings is None or not settings["voice_schedule_break"]:
                continue
            
            current_time = datetime.datetime.now(pytz.timezone(settings['time_zone']))
            if current_time.hour == settings['break_hours'] and current_time.minute == settings['break_minutes']:
                vc = discord.utils.get(self.bot.voice_clients, guild=guild)
                if (vc and vc.is_connected()):  # If the bot is connected to a voice channel in this guild
                    vc.stop()  # Stop any currently playing audio
                    await asyncio.sleep(0.5)
                    scheduled_break_text = random.choice(self.scheduled_break_messages)
                    await self.play_greeting_experimental(vc, scheduled_break_text)

    @tasks.loop(minutes=1)  # Check the time every minute
    async def break_time(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            settings = await self.get_cached_guild_settings(guild_id)

            if settings is None or not settings["voice_schedule_break"]:
                continue
            
            
            current_time = datetime.datetime.now(pytz.timezone(settings['time_zone']))
            # if current_time.minute % 5 == 0:  # If the current minute is a multiple of 5 **FOR TESTING PURPOSES**
            if current_time.minute == 0 and current_time.hour % 2 == 0:
                vc = discord.utils.get(self.bot.voice_clients, guild=guild)
                if vc and vc.is_connected():
                    vc.stop()
                    await asyncio.sleep(0.5)
                    break_text = random.choice(self.break_messages)
                    await self.play_greeting_experimental(vc, break_text)

    async def play_dj_announcement(self, guild):
        vc = discord.utils.get(self.bot.voice_clients, guild=guild)
        if vc and vc.is_connected():
            vc.stop()
            await asyncio.sleep(0.5)
            dj_announcement_text = "DJ KT is on the decks!"
            await self.play_greeting_experimental(vc, dj_announcement_text)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        with tracer.start_as_current_span("on_voice_state_update"):
            try:
                guild_id = str(member.guild.id)
                settings = await self.get_cached_guild_settings(guild_id)
                
                display_name = member.display_name
                greeting_text = random.choice(self.greetings).format(username=display_name)

                if settings is None or not settings["voice_greeting"]:
                    return
                
                async with self._voice_state_lock:
                    # User switched voice channels
                    if before.channel is not None and after.channel is not None and before.channel != after.channel:
                        vc = discord.utils.get(self.bot.voice_clients, guild=member.guild)
                        if vc:
                            await vc.move_to(after.channel)  # Move the bot to the new channel
                            if not vc.is_playing():
                                await self.play_greeting_experimental(vc, greeting_text)
                            else:
                                print(f"Skipped greeting for {member} as audio is already playing.")

                    # User joined a voice channel
                    elif before.channel is None and after.channel is not None:
                        vc = discord.utils.get(self.bot.voice_clients, guild=member.guild)
                        if not vc:
                            vc = await after.channel.connect()
                        if not vc.is_playing():
                            await self.play_greeting_experimental(vc, greeting_text)
                        else:
                            print(f"Skipped greeting for {member} as audio is already playing.")
                    
                    # User left a voice channel
                    elif before.channel is not None and after.channel is None:
                        vc = discord.utils.get(self.bot.voice_clients, guild=member.guild)
                        if vc and len(before.channel.members) == 1:
                            await vc.disconnect()
                            print(f"Disconnected from voice channel in guild {member.guild.name}")
            
            except Exception as e:
                error_data = {"data":{
                    "type": "error",
                    "description": str(e),
                }}
                Starfire.log(error_data)


    