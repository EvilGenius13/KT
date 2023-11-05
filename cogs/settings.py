import discord
from discord.ext import commands
from discord.ui import Button, View

class Settings(commands.Cog):
    def __init__(self, bot, voice_events_cog):
        self.bot = bot
        self.voice_events_cog = voice_events_cog
        
    @commands.command()
    async def button_test(self, ctx):
        button = Button(label="Click me!", style=discord.ButtonStyle.green, emoji="👋")
        button2 = Button(label="Don't click me!", style=discord.ButtonStyle.red, emoji="🚫")
        button3 = Button(label="Steam Page", style=discord.ButtonStyle.url, url="https://store.steampowered.com/app/730/CounterStrike_Global_Offensive/")
        view = View()
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        user = ctx.message.author
        await ctx.send(f"Hey {user.mention}", view=view)
    
    @commands.command()
    async def button_hello(self, ctx):
        button = Button(label="Click me!", style=discord.ButtonStyle.green, emoji="👋")
        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Hi!")
        button.callback = button_callback
        view = View()
        view.add_item(button)
        user = ctx.message.author
        await ctx.send(f"Hey {user.mention}", view=view)

    @commands.command()
    async def toggle_voice_settings(self, ctx):
        button = Button(
        label=f"Voice Greeting = {'On' if self.voice_events_cog.greeting_state else 'Off'}",
        style=discord.ButtonStyle.green if self.voice_events_cog.greeting_state else discord.ButtonStyle.red,
        custom_id="toggle_voice_greeting"
        )
        button2 = Button(
            label=f"Checkin = {'On' if self.voice_events_cog.checkin_state else 'Off'}",
            style=discord.ButtonStyle.green if self.voice_events_cog.checkin_state else discord.ButtonStyle.red,
            custom_id="toggle_checkin"
        )
        button3 = Button(
            label=f"Recurring = {'On' if self.voice_events_cog.recurring_state else 'Off'}",
            style=discord.ButtonStyle.green if self.voice_events_cog.recurring_state else discord.ButtonStyle.red,
            custom_id="toggle_recurring"
        )

        async def button_callback(interaction: discord.Interaction):
          custom_id = interaction.data['custom_id']
          print(f'{self.voice_events_cog.greeting_state}, {self.voice_events_cog.checkin_state}, {self.voice_events_cog.recurring_state}')

          if custom_id == "toggle_voice_greeting":
              self.voice_events_cog.greeting_state = not self.voice_events_cog.greeting_state
              button.label = f"Voice Greeting = {'On' if self.voice_events_cog.greeting_state else 'Off'}"
              button.style = discord.ButtonStyle.green if self.voice_events_cog.greeting_state else discord.ButtonStyle.red
          elif custom_id == "toggle_checkin":
              self.voice_events_cog.checkin_state = not self.voice_events_cog.checkin_state
              button2.label = f"Checkin = {'On' if self.voice_events_cog.checkin_state else 'Off'}"
              button2.style = discord.ButtonStyle.green if self.voice_events_cog.checkin_state else discord.ButtonStyle.red  # Corrected button reference
          elif custom_id == "toggle_recurring":
              self.voice_events_cog.recurring_state = not self.voice_events_cog.recurring_state
              button3.label = f"Recurring = {'On' if self.voice_events_cog.recurring_state else 'Off'}"
              button3.style = discord.ButtonStyle.green if self.voice_events_cog.recurring_state else discord.ButtonStyle.red  # Corrected button reference

          await interaction.response.edit_message(view=view)  # Update the message with the new view

        button.callback = button_callback
        button2.callback = button_callback
        button3.callback = button_callback

        view = View()
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        await ctx.send("Click the button to toggle voice greetings.", view=view)