import discord
from discord.ext import commands

class TextCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  async def ping(self, ctx):
    await ctx.send('pong')
  
