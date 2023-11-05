import discord
from discord.ext import commands
import requests
import json

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
            await cog.fetch_game_details(ctx, self.app_id)
        else:
            # Respond to the interaction with an error message
            await interaction.response.send_message('Failed to fetch game details.')

class WatchlistView(discord.ui.View):
    def __init__(self, watchlist):
        super().__init__()
        for item in watchlist:
            button = FetchButton(label=item['game_name'], app_id=item['app_id'])
            self.add_item(button)


def save_watchlist(watchlist_data):
    with open('watchlist.json', 'w') as f:
        json.dump(watchlist_data, f)

def load_watchlist():
    try:
        with open('watchlist.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def add_to_watchlist(watchlist_data, app_id, game_name):
    watchlist_data.append({
        'app_id': app_id,
        'game_name': game_name
    })
    save_watchlist(watchlist_data)

def remove_from_watchlist(watchlist_data, app_id):
    watchlist_data[:] = [item for item in watchlist_data if item['app_id'] != app_id]
    save_watchlist(watchlist_data)

def is_on_watchlist(watchlist_data, app_id):
    return any(item['app_id'] == app_id for item in watchlist_data)

class SteamCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fetch_game_details(self, ctx, arg):
        try:
            response = requests.get(
                f"https://store.steampowered.com/api/appdetails?appids={arg}"
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_message = f"Error: {e}"
            await ctx.send(error_message)  # Corrected to ctx.send instead of self.send
            return

        data = response.json()

        if arg in data:
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

            watchlist_data = load_watchlist()
            on_watchlist = is_on_watchlist(watchlist_data, arg)
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
                    remove_from_watchlist(watchlist_data, arg)
                    await interaction.response.send_message("Removed from Watchlist!")
                else:
                    add_to_watchlist(watchlist_data, arg, game_name)
                    await interaction.response.send_message("Added to Watchlist!")

            button.callback = button_callback

            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button2)

            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("Game not found")
    
    @commands.command()
    async def fetch(self, ctx, arg):
        await self.fetch_game_details(ctx, arg)

    @commands.command()
    async def watchlist(self, ctx):
        watchlist = load_watchlist()

        if not watchlist:
            await ctx.send('Watchlist is empty')
            return

        view = WatchlistView(watchlist)
        # watchlist_text = '\n'.join([f"App ID: {item['app_id']} | Game Name: {item['game_name']}" for item in watchlist])
        # await ctx.send(f'**Watchlist**:\n{watchlist_text}', view=view)
        await ctx.send(view=view)
    