import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from db.db import get_guild_settings, update_guild_settings
from telemetry.axiom_setup import AxiomHelper

axiom = AxiomHelper()
class Settings(commands.Cog):
    def __init__(self, bot, voice_events_cog, session):
        self.bot = bot
        self.voice_events_cog = voice_events_cog
        self.session = session

    @commands.command()
    async def register(self, ctx):
        guild_id = str(ctx.guild.id)
        guild_name = ctx.guild.name

        # Check if guild is already registered
        try:
            result = self.session.execute("""
                SELECT guild_id FROM bot_keyspace.guilds WHERE guild_id = %s
                """, (guild_id,))
            if result.one():
                # Guild is already registered
                await ctx.send(f"Your guild, {guild_name}, is already registered.")
                axiom.send_event([{"type": "registration", "status": "already_registered", "guild_id": guild_id, "guild_name": guild_name}])
                return
            else:
                axiom.send_event([{"type": "registration", "status": "success", "guild_id": guild_id, "guild_name": guild_name}])
        except Exception as e:
            raise
        
        # Register guild if not already registered
        try:
            self.session.execute("""
                INSERT INTO bot_keyspace.guilds (
                    guild_id, 
                    guild_name, 
                    voice_greeting,
                    voice_break_time,
                    voice_schedule_break
                )
                VALUES (%s, %s, %s, %s, %s)
                """, (guild_id, guild_name, False, False, False))
            await ctx.send(f"Registered {guild_name} successfully.")
        except Exception as e:
            await ctx.send(f"Error registering {guild_name}: {e}")

    @commands.command()
    async def toggle_voice_settings(self, ctx):
        guild_id = str(ctx.guild.id)
        settings = await get_guild_settings(self.session, guild_id)

        if settings is None:
            await ctx.send("Guild settings not found. Please register your guild first.")
            return

        def create_button(label, style, custom_id):
            return Button(label=label, style=style, custom_id=custom_id)

        button = create_button(
            f"Voice Greeting = {'On' if settings['voice_greeting'] else 'Off'}",
            discord.ButtonStyle.green if settings['voice_greeting'] else discord.ButtonStyle.red,
            "toggle_voice_greeting"
        )
        button2 = create_button(
            f"Checkin = {'On' if settings['voice_break_time'] else 'Off'}",
            discord.ButtonStyle.green if settings['voice_break_time'] else discord.ButtonStyle.red,
            "toggle_checkin"
        )
        button3 = create_button(
            f"Recurring = {'On' if settings['voice_schedule_break'] else 'Off'}",
            discord.ButtonStyle.green if settings['voice_schedule_break'] else discord.ButtonStyle.red,
            "toggle_recurring"
        )

        async def button_callback(interaction: discord.Interaction):
            custom_id = interaction.data["custom_id"]
            guild_id = str(ctx.guild.id)

            # Map custom_id to the actual settings key
            id_to_setting_key = {
                "toggle_voice_greeting": "voice_greeting",
                "toggle_checkin": "voice_break_time",
                "toggle_recurring": "voice_schedule_break"
            }

            # Fetch current settings
            current_settings = await get_guild_settings(self.session, guild_id)

            # Determine which setting to toggle and update
            setting_key = id_to_setting_key.get(custom_id)
            if setting_key:
                current_settings[setting_key] = not current_settings[setting_key]

                # Update the settings in the database
                await update_guild_settings(self.session, guild_id, current_settings)

                # Update button labels and styles
                for btn in view.children:
                    if btn.custom_id == custom_id:
                        btn.label = f"{setting_key.replace('_', ' ').capitalize()} = {'On' if current_settings[setting_key] else 'Off'}"
                        btn.style = discord.ButtonStyle.green if current_settings[setting_key] else discord.ButtonStyle.red
                        break

            await interaction.response.edit_message(view=view)

        # Set the callback for each button
        button.callback = button_callback
        button2.callback = button_callback
        button3.callback = button_callback

        # Create and display the view with buttons
        view = View()
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)

        await ctx.send("Click the button to toggle voice settings.", view=view)

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