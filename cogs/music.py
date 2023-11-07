import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}  # Dictionary to store the queue of songs for each guild

    def get_guild_queue(self, guild):
        if guild.id not in self.song_queue:
            self.song_queue[guild.id] = []
        return self.song_queue[guild.id]

    async def play_next_in_queue(self, guild):
        queue = self.get_guild_queue(guild)
        if queue:
            next_song = queue.pop(0)
            await self.play_song(guild, next_song)

    async def play_song(self, guild, song):
        channel = song['channel']
        vc = discord.utils.get(self.bot.voice_clients, guild=guild)
        if not vc:
            vc = await channel.connect()
        
        # Define the after function to play the next song in the queue
        def after_playing(error):
            fut = asyncio.run_coroutine_threadsafe(self.play_next_in_queue(guild), self.bot.loop)
            try:
                fut.result()
            except:
                pass  # Handle errors here if needed
        
        vc.play(discord.FFmpegPCMAudio(song['url']), after=after_playing)

    @commands.command(name='play', help='Plays a song from YouTube')
    async def play(self, ctx, *, url):
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
            'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info['url']
            
            # Add song to queue
            queue = self.get_guild_queue(ctx.guild)
            queue.append({'url': download_url, 'channel': channel})
            
            # If a song is not currently playing, start playing
            if not vc.is_playing() and not vc.is_paused():
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
