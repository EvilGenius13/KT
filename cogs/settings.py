import discord
from discord.ext import commands
from discord.ui import Button, View


class Settings(commands.Cog):
    def __init__(self, bot, voice_events_cog, session):
        self.bot = bot
        self.voice_events_cog = voice_events_cog
        self.session = session

    @commands.command()
    async def register(self, ctx):
        guild_id = str(ctx.guild.id)
        guild_name = ctx.guild.name

        try:
            self.session.execute("""
                INSERT INTO bot_keyspace.guilds (guild_id, guild_name, voice_setting)
                VALUES (%s, %s, %s)
                """, (guild_id, guild_name, False))
            await ctx.send(f"Registered {guild_name} successfully.")
        except Exception as e:
            await ctx.send(f"Error registering {guild_name}: {e}")

    @commands.command()
    async def toggle_voice_settings(self, ctx):
        button = Button(
            label=f"Voice Greeting = {'On' if self.voice_events_cog.greeting_state else 'Off'}",
            style=discord.ButtonStyle.green
            if self.voice_events_cog.greeting_state
            else discord.ButtonStyle.red,
            custom_id="toggle_voice_greeting",
        )
        button2 = Button(
            label=f"Checkin = {'On' if self.voice_events_cog.checkin_state else 'Off'}",
            style=discord.ButtonStyle.green
            if self.voice_events_cog.checkin_state
            else discord.ButtonStyle.red,
            custom_id="toggle_checkin",
        )
        button3 = Button(
            label=f"Recurring = {'On' if self.voice_events_cog.recurring_state else 'Off'}",
            style=discord.ButtonStyle.green
            if self.voice_events_cog.recurring_state
            else discord.ButtonStyle.red,
            custom_id="toggle_recurring",
        )

        async def button_callback(interaction: discord.Interaction):
            custom_id = interaction.data["custom_id"]
            print(
                f"{self.voice_events_cog.greeting_state}, {self.voice_events_cog.checkin_state}, {self.voice_events_cog.recurring_state}"
            )

            if custom_id == "toggle_voice_greeting":
                self.voice_events_cog.greeting_state = (
                    not self.voice_events_cog.greeting_state
                )
                button.label = f"Voice Greeting = {'On' if self.voice_events_cog.greeting_state else 'Off'}"
                button.style = (
                    discord.ButtonStyle.green
                    if self.voice_events_cog.greeting_state
                    else discord.ButtonStyle.red
                )
            elif custom_id == "toggle_checkin":
                self.voice_events_cog.checkin_state = (
                    not self.voice_events_cog.checkin_state
                )
                button2.label = f"Checkin = {'On' if self.voice_events_cog.checkin_state else 'Off'}"
                button2.style = (
                    discord.ButtonStyle.green
                    if self.voice_events_cog.checkin_state
                    else discord.ButtonStyle.red
                )  # Corrected button reference
            elif custom_id == "toggle_recurring":
                self.voice_events_cog.recurring_state = (
                    not self.voice_events_cog.recurring_state
                )
                button3.label = f"Recurring = {'On' if self.voice_events_cog.recurring_state else 'Off'}"
                button3.style = (
                    discord.ButtonStyle.green
                    if self.voice_events_cog.recurring_state
                    else discord.ButtonStyle.red
                )  # Corrected button reference

            await interaction.response.edit_message(
                view=view
            )  # Update the message with the new view

        button.callback = button_callback
        button2.callback = button_callback
        button3.callback = button_callback

        view = View()
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        await ctx.send("Click the button to toggle voice greetings.", view=view)

    @commands.command()
    async def set_scheduled_break(self, ctx, arg):
        try:
            hours, minutes = map(int, arg.split(":"))
            self.voice_events_cog.current_hours = hours
            self.voice_events_cog.current_minutes = minutes
            await ctx.send(
                f"Set scheduled break to {hours}:{minutes}. This will take effect in the next minute."
            )
        except ValueError as e:
            if 'Hours must be between 0 and 23' in str(e) or 'Minutes must be between 0 and 59' in str(e):
                await ctx.send(str(e))
            else:
                await ctx.send("Invalid time format. Please use HH:MM format.")
        except Exception as e:
            await ctx.send("An error occurred while setting the scheduled break time.")