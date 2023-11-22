import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from telemetry.tracing_setup import tracer
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}  # Dictionary to store the queue of songs for each guild

    def get_guild_queue(self, guild):
        if guild.id not in self.song_queue:
            self.song_queue[guild.id] = []
        return self.song_queue[guild.id]

    def get_full_path(self, relative_path):
        # This assumes your bot's main script is in the root of your project directory.
        # If this is not the case, you need to adjust this accordingly.
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.normpath(os.path.join(root_dir, relative_path))
    
    async def play_next_in_queue(self, guild):
        queue = self.get_guild_queue(guild)
        if queue:
            next_song = queue.pop(0)
            vc = discord.utils.get(self.bot.voice_clients, guild=guild)
            if vc:
                full_path = self.get_full_path(next_song['filename'])
                audio_source = discord.FFmpegPCMAudio(full_path)
                # You can set the volume here (1.0 is the default volume, 0.5 for half volume, etc.)
                audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.4) 
                print(f"Playing {full_path} at volume: {audio_source.volume}")
                vc.play(audio_source, after=lambda e: self.after_playing(guild, full_path))
        
    def after_playing(self, guild, full_path):
        # Check if the file exists before trying to remove it
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except OSError as e:
                print(f"Error: {full_path} : {e.strerror}")
        else:
            print(f"File not found: {full_path}")

        # Schedule the next song to be played
        asyncio.run_coroutine_threadsafe(self.play_next_in_queue(guild), self.bot.loop)

    @commands.command(name='dj', help='What can I play for you?')
    async def dj(self, ctx):
        await ctx.send("What can I play for you? Copy and paste a YouTube URL like this: `!play https://www.youtube.com/watch?v=dQw4w9WgXcQ`")
    
    @commands.command(name='play', help='Plays a song from YouTube')
    async def play(self, ctx, *, url):
        with tracer.start_as_current_span("play_music_command"):
            author = ctx.message.author
            if not author.voice:
                await ctx.send("You are not connected to a voice channel.")
                return

            channel = author.voice.channel
            vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

            if not vc:
                vc = await channel.connect()

            # Now `vc` is defined, and we can safely check if it's playing or paused
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': self.get_full_path('downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s'),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Explicitly set the filename to the .mp3 version
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3')
                
                # Add song to queue
                queue = self.get_guild_queue(ctx.guild)
                queue.append({'filename': filename, 'channel': channel})
                print(f"Added {filename} to queue for {ctx.guild.name}")
                
                # If a song is not currently playing, start playing
                if not vc.is_playing() and not vc.is_paused():
                    await ctx.send("DJ KT is on the decks!")
                    await self.play_next_in_queue(ctx.guild)
                else:
                    await ctx.send("Song added to the queue.")

    @commands.command(name='pause', help='Pauses the currently playing song')
    async def pause(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("Paused the song.")
        else:
            await ctx.send("No song is currently playing.")

    @commands.command(name='resume', help='Resumes the currently paused song')
    async def resume(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("Resumed the song.")
        else:
            await ctx.send("No song is currently paused.")

    @commands.command(name='stop', help='Stops the currently playing song and clears the queue')
    async def stop(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            self.song_queue[ctx.guild.id] = []  # Clear the queue
            await ctx.send("Stopped the song and cleared the queue.")
        else:
            await ctx.send("No song is currently playing.")
