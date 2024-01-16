import discord
from discord.ext import commands, tasks
from initializers.axiom_setup import AxiomHelper
from datetime import datetime, timedelta
import pytz

axiom = AxiomHelper()

class TextCommands(commands.Cog):
  GAME_NIGHT_TASK_ID = 'game_night_task'
  running_tasks = {}
  
  def __init__(self, bot):
    self.bot = bot
    self.game_night.start()

  
  def cog_unload(self):
        self.game_night.cancel()  # Cancel the task loop when the cog is unloaded
  
  @staticmethod
  def calculate_next_game_night_time(current_time):
      """
      Calculates the next occurrence of game night in EST.
      Game nights are on Tuesday and Thursday at 7:30 PM EST.
      """
      target_hour = 19  # 7:30 PM in 24-hour format
      target_minute = 30

      # Convert current time to Eastern Standard Time (EST)
      eastern = pytz.timezone('America/New_York')
      current_time = current_time.astimezone(eastern)

      # If current time is past 7:30 PM EST, start calculation from the next day
      if current_time.hour > target_hour or (current_time.hour == target_hour and current_time.minute > target_minute):
          current_time += timedelta(days=1)

      # Reset time to 7:30 PM EST
      next_game_night = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

      # Find the next Tuesday (1) or Thursday (3)
      while next_game_night.weekday() != 1 and next_game_night.weekday() != 3:
          next_game_night += timedelta(days=1)

      # Convert back to UTC for asyncio.sleep_until
      return next_game_night.astimezone(pytz.utc)
  
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

  @tasks.loop(hours=24)
  async def game_night(self):
      if self.__class__.GAME_NIGHT_TASK_ID in self.__class__.running_tasks:
            data = [{"type": "error", "value": "game night task already running"}]
            axiom.send_event(data)
            return
      
      next_game_night = self.calculate_next_game_night_time(datetime.now())
      await discord.utils.sleep_until(next_game_night)
      await self.announce_game_night()

      self.__class__.running_tasks[self.__class__.GAME_NIGHT_TASK_ID] = self.game_night

  async def announce_game_night(self):
      embed = discord.Embed(title="Game Night!", description="It's time for our game night! Join us in the 'General' voice channel.", color=0xea1010)
      specific_guild_id = 176521576882110464  # Replace with your specific guild's ID
      specific_channel_id = 176521576882110464  # Replace with your specific channel's ID
      guild = self.bot.get_guild(specific_guild_id)
      if guild:
          channel = guild.get_channel(specific_channel_id)
          if channel:
              await channel.send(embed=embed)
      self.__class__.running_tasks.pop(self.__class__.GAME_NIGHT_TASK_ID, None)

