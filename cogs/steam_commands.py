import discord
from discord.ext import commands
import requests
import json
from telemetry.tracing_setup import tracer


class FetchButton(discord.ui.Button):
    def __init__(self, label, app_id):
        super().__init__(label=label, style=discord.ButtonStyle.blurple)
        self.app_id = app_id

    async def callback(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog('SteamCommands')
        if cog is not None:
            # Defer the interaction response
            await interaction.response.defer()
            
            # Create a context for the command invocation
            message = interaction.message
            ctx = await cog.bot.get_context(message)
            
            # Call the fetch_game_details method
            await cog.steam_fetch(ctx, self.app_id)
        else:
            # Respond to the interaction with an error message
            await interaction.response.send_message('Failed to fetch game details.')

class WatchlistView(discord.ui.View):
    def __init__(self, watchlist):
        super().__init__()
        for item in watchlist:
            button = FetchButton(label=item['app_name'], app_id=item['app_id'])
            self.add_item(button)

class SteamCommands(commands.Cog):
    def __init__(self, bot, session):
        self.bot = bot
        self.session = session
        
    @commands.command()
    async def steam_fetch(self, ctx, arg):
        guild_id = str(ctx.guild.id)
        with tracer.start_as_current_span("steam_fetch", attributes={"type": "command"}):
            with tracer.start_as_current_span("http_request"):
                try:
                    response = requests.get(
                        f"https://store.steampowered.com/api/appdetails?appids={arg}"
                    )
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    error_message = f"Error: {e}"
                    await ctx.send(error_message)
                    return

            with tracer.start_as_current_span("process_response"):
                data = response.json()

                if arg not in data:
                    await ctx.send("Game not found")
                    return
                
                game_data = data[arg]["data"]
                game_name = game_data.get("name", "Name not found")
                header_image = game_data.get("header_image", "Image not found")

                price_overview = game_data.get("price_overview", None)
                
                if price_overview:
                    final_formatted = price_overview.get(
                        "final_formatted", "Final price not found"
                    )
                    discount = price_overview.get("discount_percent", "No current discount")
                    description = game_data.get("short_description", "No description found")
                else:
                    final_formatted = "Price not listed"
                    discount = "0"
                    description = "No description found"
                    release_date = "No release date found"

                release_date_data = game_data.get("release_date", {})
                is_coming_soon = release_date_data.get("coming_soon", False)
                release_date = release_date_data.get("date", "No release date found")

                embed = discord.Embed(title=f"Game Name: {game_name}", color=0xea1010)
                if is_coming_soon:
                    embed.add_field(name="Release Date", value="Coming Soon", inline=True)
                else:
                    embed.add_field(name="Release Date", value=release_date, inline=True)
                embed.add_field(name="Description", value=description, inline=False)
                embed.set_image(url=header_image)
                embed.add_field(name="Current Price", value=final_formatted, inline=True)
                embed.add_field(name="Discount", value=f"**{discount}%**", inline=True)
                embed.set_thumbnail(url="https://i.postimg.cc/3R4fnw0x/twsgirl.png")
            
            with tracer.start_as_current_span("load_watchlist"):
                watchlist_data = self._load_watchlist(guild_id)
                on_watchlist = self._is_on_watchlist(guild_id, arg)

            with tracer.start_as_current_span("setup_buttons"):
                button_label = "Remove from Watchlist" if on_watchlist else "Add to Watchlist"
                button_style = discord.ButtonStyle.red if on_watchlist else discord.ButtonStyle.green
                button = discord.ui.Button(
                            label=button_label,
                            style=button_style,
                            emoji="👀",
                            custom_id="watchlist",
                        )
                button2 = discord.ui.Button(
                            label="Steam Page",
                            style=discord.ButtonStyle.url,
                            url=f"https://store.steampowered.com/app/{arg}/",
                        )
                async def button_callback(interaction: discord.Interaction):
                    if on_watchlist:
                        self._remove_from_watchlist(guild_id, arg)
                        await interaction.response.send_message("Removed from Watchlist!")
                    else:
                        self._add_to_watchlist(guild_id, arg, game_name)
                        await interaction.response.send_message("Added to Watchlist!")

                button.callback = button_callback
                
            with tracer.start_as_current_span("send_response"):
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)

                await ctx.send(embed=embed, view=view)

    @commands.command()
    async def fetch(self, ctx, arg):
        await self.steam_fetch(ctx, arg)

    @commands.command()
    async def watchlist(self, ctx):
        guild_id = str(ctx.guild.id)
        with tracer.start_as_current_span("watchlist", attributes={"type": "command"}) as parent_span:
            with tracer.start_as_current_span("watchlist_db_call", attributes={"operation": "database"}):
                watchlist = self._load_watchlist(guild_id)

            with tracer.start_as_current_span("send_watchlist", attributes={"operation": "message_send"}):
                if not watchlist:
                    await ctx.send('Watchlist is empty')
                    return

                view = WatchlistView(watchlist)
                await ctx.send(view=view)
    
    def _load_watchlist(self, guild_id):
        try: 
            query = "SELECT app_id, app_name FROM wishlists WHERE guild_id = %s"
            rows = self.session.execute(query, [guild_id])
            watchlist = [{'app_id': row.app_id, 'app_name': row.app_name} for row in rows]
            return watchlist
        except Exception as e:
            print(f"Error in _load_watchlist: {e}")
            return []
        
    def _add_to_watchlist(self, guild_id, app_id, game_name):
        try:
            query = """
            INSERT INTO wishlists (guild_id, app_id, app_name)
            VALUES (%s, %s, %s)
            """
            self.session.execute(query, (guild_id, app_id, game_name))
        except Exception as e:
            print(f"Error adding to watchlist: {e}")

    def _remove_from_watchlist(self, guild_id, app_id):
        try:
            query = "DELETE FROM wishlists WHERE guild_id = %s AND app_id = %s"
            self.session.execute(query, (guild_id, app_id))
        except Exception as e:
            print(f"Error removing from watchlist: {e}")

    def _is_on_watchlist(self, guild_id, app_id):
        try:
            query = "SELECT app_id FROM wishlists WHERE guild_id = %s AND app_id = %s"
            row = self.session.execute(query, (guild_id, app_id)).one()
            return row is not None
        except Exception as e:
            print(f"Error checking watchlist: {e}")
            return False