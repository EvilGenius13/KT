import discord
from discord.ext import commands, tasks
from telemetry.tracing_setup import tracer
from telemetry.axiom_setup import AxiomHelper
import datetime

axiom = AxiomHelper()

class XpSystem(commands.Cog):
    def __init__(self, bot, session):
        self.bot = bot
        self.session = session

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        current_xp, current_level = self._load_user_xp(message.guild.id, message.author.id)
        xp_to_add = 5  # Or calculate based on message content/length

        with tracer.start_as_current_span("on_message", attributes={"type": "command"}):
            with tracer.start_as_current_span("add_xp"):
                new_xp = current_xp + xp_to_add
                new_level = self._level_for_xp(new_xp)

                self._update_user_xp_and_level(message.guild.id, message.author.id, new_xp, new_level)

                xp_data = [{
                    "type": "xp",
                    "guild_id": str(message.guild.id),
                    "user_id": str(message.author.id),
                    "current_xp": current_xp,
                    "new_xp": new_xp,
                    "current_level": current_level,
                    "new_level": new_level
                }]
                axiom.send_event(xp_data)

                if new_level > current_level:
                    await message.channel.send(f"{message.author.mention} You've leveled up to level {new_level}!")

    def _level_for_xp(self, xp, base_xp=100, multiplier=0.5):
        level = 1
        while self._xp_for_level(level + 1, base_xp, multiplier) <= xp:
            level += 1
        return level

    def _xp_for_level(self, level, base_xp=100, multiplier=0.5):
        if level <= 1:
            return 0
        return int(base_xp * (level ** multiplier))

    def _update_user_xp_and_level(self, guild_id, user_id, new_xp, new_level):
        guild_id_str = str(guild_id)
        user_id_str = str(user_id)
        current_time = datetime.datetime.now()

        with tracer.start_as_current_span("update_user_xp_and_level", attributes={"type": "db"}):
            with tracer.start_as_current_span("update_user_xp_and_level_query"):
                query = """
                INSERT INTO user_xp (guild_id, user_id, xp, level, last_updated)
                VALUES (%s, %s, %s, %s, %s)
                USING TTL 604800
                """
                self.session.execute(query, [guild_id_str, user_id_str, new_xp, new_level, current_time])

    def _load_user_xp(self, guild_id, user_id):
        guild_id_str = str(guild_id)
        user_id_str = str(user_id)

        with tracer.start_as_current_span("load_user_xp", attributes={"type": "db"}):
            with tracer.start_as_current_span("load_user_xp_query"):
                query = """
                SELECT xp, level
                FROM user_xp
                WHERE guild_id = %s AND user_id = %s
                """
                result = self.session.execute(query, [guild_id_str, user_id_str])
                row = result.one()
                if row is None:
                    return 0, 0
                return row.xp, row.level
