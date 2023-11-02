import discord
from discord.ext import commands

class TextCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  async def hello(self, ctx):
    user = ctx.message.author
    await ctx.send(f'Hey {user.mention}')
  
