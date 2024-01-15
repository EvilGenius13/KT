import discord
from discord.ext import commands
import os
from openai import OpenAI
import time
import datetime

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

from initializers.tracing_setup import tracer
from initializers.axiom_setup import AxiomHelper

axiom = AxiomHelper()


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = 'gpt-3.5-turbo-1106'
        self.assistant_id = os.getenv("OPENAI_ASSISTANT")
        self.last_message_time = None
        self.last_author_id = None
        self.thread_id = None

    @commands.command()
    async def tws_chat(self, ctx, *, message):
        with tracer.start_as_current_span("tws_chat", attributes={"type": "command"}):
            user_name = ctx.author.name
            current_time = datetime.datetime.now()
            time_diff = (current_time - self.last_message_time).total_seconds() if self.last_message_time else 61
            author_id = ctx.author.id

            if time_diff > 60 or author_id != self.last_author_id:
                my_thread = client.beta.threads.create()
                self.thread_id = my_thread.id
            
            my_thread_id = self.thread_id

            try:
                with tracer.start_as_current_span("openai", attributes={"type": "openai"}):
                    my_thread_message = client.beta.threads.messages.create(
                        thread_id = my_thread_id,
                        role = "user",
                        content = message,
                    )

                    my_run = client.beta.threads.runs.create(
                        thread_id = my_thread_id,
                        assistant_id = str(self.assistant_id),
                        instructions = f"Please address the user as {user_name}",
                    )
                    
                    while my_run.status in ["queued", "in_progress"]:
                        keep_retrieving_run = client.beta.threads.runs.retrieve(
                            thread_id=my_thread_id,
                            run_id=my_run.id
                        )
                        print(f"Run status: {keep_retrieving_run.status}")
                        time.sleep(1)

                        if keep_retrieving_run.status == "completed":
                            print("\n")


                            all_messages = client.beta.threads.messages.list(
                                thread_id=my_thread_id
                            )

                            data = [{"type": "command", "value": "chat", "user": str(ctx.author.id), "user-message": message, "kt-reply": all_messages.data[0].content[0].text.value}]
                            axiom.send_event(data)
                            break
                        elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
                            pass
                        else:
                            print(f"Run status: {keep_retrieving_run.status}")
                            break
                    
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
                        description=all_messages.data[0].content[0].text.value,
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
            data = [{"type": "command", "value": "tws_chat", "user": str(ctx.author.id), "user-message": message, "kt-reply": all_messages.data[0].content[0].text.value}]
            axiom.send_event(data)
            self.last_message_time = current_time
            self.last_author_id = author_id

    @commands.command()
    async def chat(self, ctx, *, message):
        with tracer.start_as_current_span("chat", attributes={"type": "command"}):
            user_name = ctx.author.name
            try:
                with tracer.start_as_current_span("openai", attributes={"type": "openai"}):
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are a friendly helpful assistant named KT. You are part of team Time Well Spent (TWS). You can also address the user as {user_name}"
                            },
                            {
                                "role": "user",
                                "content": message
                            }
                        ],
                        temperature=0.5,
                        max_tokens=256,
                        top_p=0.5,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
                    answer = response.choices[0].message.content

            except Exception as e:
                print(f"Error during OpenAI API call: {type(e).__name__}: {e}")
                await ctx.send("Sorry, I encountered an error while processing your request.")
                return

            try:
                with tracer.start_as_current_span("discord", attributes={"type": "discord"}):
                    embed = discord.Embed(
                        title="Chat",
                        description=answer,
                        color=0xEA1010,
                    )
                    embed.set_footer(text=f"Response for {ctx.author.display_name}")
                    await ctx.send(embed=embed)
            except Exception as e:
                print(f"Error during Discord operation: {type(e).__name__}: {e}")
                await ctx.send("An error occurred while sending the message. Please try again.")
            
            data = [{"type": "command", "value": "chat", "user": str(ctx.author.id), "user-message": message, "kt-reply": answer}]
            axiom.send_event(data)
