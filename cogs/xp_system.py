import discord
from discord.ext import commands, tasks
from telemetry.tracing_setup import tracer
from telemetry.axiom_setup import AxiomHelper

axiom = AxiomHelper()

class XpSystem(commands.Cog):
    def __init__(self, bot, session):
        self.bot = bot
        self.session = session

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        current_xp = self._load_user_xp(message.guild.id, message.author.id)
        xp_to_add = 5  # Or calculate based on message content/length

        with tracer.start_as_current_span("on_message", attributes={"type": "command"}):
            with tracer.start_as_current_span("add_xp"):
                new_xp = current_xp + xp_to_add
                self._add_xp(message.guild.id, message.author.id, new_xp)

                current_level = self._level_for_xp(current_xp)
                new_level = self._level_for_xp(new_xp)

                if new_level > current_level:
                    await message.channel.send(f"{message.author.mention} You've leveled up to level {new_level}!")

    def _xp_for_level(self, level, base_xp=100, multiplier=1.5):
        if level <= 1:
            return 0
        return int(base_xp * (level ** multiplier))

    def _level_for_xp(self, xp, base_xp=100, multiplier=1.5):
        level = 1
        while self._xp_for_level(level + 1, base_xp, multiplier) <= xp:
            level += 1
        return level

    def _add_xp(self, guild_id, user_id, new_xp):
        with tracer.start_as_current_span("add_xp", attributes={"type": "db"}):
            with tracer.start_as_current_span("add_xp_query"):
                query = """
                UPDATE user_xp
                SET xp = %s
                WHERE guild_id = %s AND user_id = %s
                """
                self.session.execute(query, [new_xp, guild_id, user_id])

    def _load_user_xp(self, guild_id, user_id):
        with tracer.start_as_current_span("load_user_xp", attributes={"type": "db"}):
            with tracer.start_as_current_span("load_user_xp_query"):
                query = """
                SELECT xp
                FROM user_xp
                WHERE guild_id = %s AND user_id = %s
                """
                result = self.session.execute(query, [guild_id, user_id])
                row = result.one()
                if row is None:
                    return 0
                return row.xp