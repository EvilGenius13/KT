import discord
from discord.ext import commands


class Modal(discord.ui.Modal, title="modal test"):
  answer = discord.ui.TextInput(label="answer", placeholder="Enter your response here")

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.send_message(f"You said {self.answer.value}")


class PokeQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def question_one(self, ctx):
        # Create a button that, when clicked, will trigger a modal
        class OpenModalButton(discord.ui.Button):
            def __init__(self):
                super().__init__(label="Answer", style=discord.ButtonStyle.primary)
            
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_modal(Modal())

        view = discord.ui.View()
        view.add_item(OpenModalButton())
        await ctx.send("Click the button to answer:", view=view)