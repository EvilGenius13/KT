import discord
from discord.ext import commands
import requests
import json
import random
from initializers.tracing_setup import tracer
from initializers.redis import r


class PokeQuizModal(discord.ui.Modal):
    def __init__(self, correct_answer, session):
        super().__init__(title="Who's that Pokémon?")
        self.correct_answer = correct_answer
        self.session = session

        # Add the TextInput to the modal
        self.answer_input = discord.ui.TextInput(
            label="Answer",
            placeholder="Enter the Pokémon's name"
        )
        self.add_item(self.answer_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_answer = self.answer_input.value.lower()

        # Fetch the current streak
        try:
            select_query = "SELECT streak FROM quiz WHERE user_id = %s"
            row = self.session.execute(select_query, (user_id)).one()
            current_streak = row.streak if row else 0
        except Exception as e:
            print(f"Error fetching quiz streak: {e}")
            current_streak = 0

        if user_answer == self.correct_answer:
            new_streak = current_streak + 1
            response_message = f"It's {self.correct_answer.capitalize()}! You got it right! Your current streak is {new_streak}!"
        else:
            response_message = f"It's {self.correct_answer.capitalize()}! Close one, maybe next time! Your streak has been reset."
            new_streak = 0

        # Update the streak in the database
        try:
            update_query = """
                INSERT INTO quiz (user_id, streak)
                VALUES (%s, %s)
                """
            self.session.execute(update_query, (user_id, new_streak))
        except Exception as e:
            print(f"Error updating quiz streak: {e}")

        await interaction.response.send_message(response_message)


class PokeQuiz(commands.Cog):
    def __init__(self, bot, session, cache_event_handler):
        self.bot = bot
        self.session = session
        self.cache_event_handler = cache_event_handler
        self.current_pokemon = None

        

    @commands.command()
    async def quiz(self, ctx):
        with tracer.start_as_current_span("quiz", attributes={"type": "command"}):
            pokedex_number = random.randint(1, 151)
            with tracer.start_as_current_span("http_request"):
                try:
                    response = requests.get(
                        f"https://pokeapi.co/api/v2/pokemon/{pokedex_number}"
                    )
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    error_message = f"Error: {e}"
                    await ctx.send(error_message)
                    return

            with tracer.start_as_current_span("process_response"):
                data = response.json()
                name = data["name"]
                self.current_pokemon = name.lower()
                image_url = data["sprites"]["front_default"]
                
                embed = discord.Embed(title="Who's that Pokemon?", color=0xea1010)
                embed.set_image(url=image_url)
        # Create a button that, when clicked, will trigger a modal
        class OpenModalButton(discord.ui.Button):
            def __init__(self, cog_instance):
                super().__init__(label="Answer", style=discord.ButtonStyle.primary)
                self.cog_instance = cog_instance
            
            async def callback(self, interaction: discord.Interaction):
                modal = PokeQuizModal(correct_answer=self.cog_instance.current_pokemon, session=self.cog_instance.session)
                await interaction.response.send_modal(modal)

        view = discord.ui.View()
        view.add_item(OpenModalButton(cog_instance=self))
        await ctx.send(embed=embed, view=view)
