import discord
import discord.ext.commands as commands
import requests
import json
import initializers.tracing_setup as tracing_setup
from initializers.axiom_setup import AxiomHelper

axiom = AxiomHelper()

class Analytics(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def steam_players(self, ctx, arg):
    with tracing_setup.tracer.start_as_current_span("steam_players", attributes={"type": "command"}):
      try:
        response = requests.get(
          f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={arg}"
        )
        response.raise_for_status()
      except requests.exceptions.RequestException as e:
        error_message = f"Error: {e}"
        await ctx.send(error_message)
        return

      data = response.json()
      if data['response']['result'] == 1:
        await ctx.send(f"{data['response']['player_count']} players are currently playing {arg}")
      else:
        await ctx.send(f"Error: {data['response']['error']}")