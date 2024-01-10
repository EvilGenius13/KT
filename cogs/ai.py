import discord
from discord.ext import commands
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

from telemetry.tracing_setup import tracer
from telemetry.axiom_setup import AxiomHelper

axiom = AxiomHelper()


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = os.getenv("OPENAI_ASSISTANT")

    @commands.command()
    async def chat(self, ctx, message):
        with tracer.start_as_current_span("chat", attributes={"type": "command"}):
            data = [{"type": "command", "value": "chat"}]
            axiom.send_event(data)

            try:
                with tracer.start_as_current_span(
                    "openai", attributes={"type": "openai"}
                ):
                    # Get the response from OpenAI Assistant
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        messages=[{"role": "user", "content": message}],
                    )
            except Exception as e:
                # Log the error type and message
                print(f"Error during OpenAI API call: {type(e).__name__}: {e}")
                await ctx.send(
                    "Sorry, I encountered an error while processing your request."
                )
                return

            try:
                with tracer.start_as_current_span(
                    "discord", attributes={"type": "discord"}
                ):
                    # Create an embed for the response
                    embed = discord.Embed(
                        title="Chat",
                        description=response.choices[0].message["content"],
                        color=0xEA1010,
                    )
                    embed.set_footer(text=f"Response for {ctx.author.display_name}")

                    # Send the embed
                    await ctx.send(embed=embed)
            except Exception as e:
                # Log the error type and message
                print(f"Error during Discord operation: {type(e).__name__}: {e}")
                await ctx.send(
                    "An error occurred while sending the message. Please try again."
                )
