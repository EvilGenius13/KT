import discord
from discord.ext import commands
from telemetry.axiom_setup import AxiomHelper

axiom = AxiomHelper()

class TextCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  async def hello(self, ctx):
    user = ctx.message.author
    data = [{"type": "command", "value": "hello_message"}]
    axiom.send_event(data)
    await ctx.send(f'Hey {user.mention}')
  
  @commands.command()
  async def settings_test(self, ctx, arg):
    if ctx.guild is not None:
      try: 
        await ctx.author.send(f'You are in guild {ctx.guild.name}')
      except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, I can't send you a DM. Please check your privacy settings.")
    else:
      await ctx.send(f"We're already talking in DMs, {ctx.author.mention}!")