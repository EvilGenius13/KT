import discord
from discord.ext import commands, tasks
from initializers.tracing_setup import tracer
from initializers.axiom_setup import AxiomHelper
import datetime
from initializers.redis import r

axiom = AxiomHelper()


class XpSystem(commands.Cog):
    LEVEL_ROLE_MAP = {
        10: 1194747774814666904,
        20: 1194748603579760842,
        30: 1194748678225809500,
        40: 1194748717257986138,
        50: 1194748786526924910,
        60: 1194748848560689153,
        70: 1194748887953576157,
        80: 1194748921344446474,
        90: 1194748981872439356,
        100: 1194749021412147251,
    }

    def __init__(self, bot, session):
        self.bot = bot
        self.session = session
        self.last_message_timestamps = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        if message.guild is None:
            return

        # Cooldown implementation
        user_id = message.author.id
        guild_id = message.guild.id
        current_time = datetime.datetime.now()

        # Cooldown Period
        cooldown_period = datetime.timedelta(seconds=5)
        last_message_time = self.last_message_timestamps.get((guild_id, user_id))

        # Check if message is within cooldown period
        if last_message_time and (current_time - last_message_time) < cooldown_period:
            return  # Skip XP processing if within cooldown
        

        current_xp, current_level = self._load_user_xp(
            message.guild.id, message.author.id
        )
        xp_to_add = 5  # Or calculate based on message content/length

        with tracer.start_as_current_span("on_message", attributes={"type": "command"}):
            with tracer.start_as_current_span("add_xp"):
                new_xp = current_xp + xp_to_add
                new_level = self._level_for_xp(new_xp)

                self._update_user_xp_and_level(
                    message.guild.id, message.author.id, new_xp, new_level
                )

                xp_data = [
                    {
                        "type": "xp",
                        "guild_id": str(message.guild.id),
                        "user_id": str(message.author.id),
                        "user_name": str(message.author.name),
                        "current_xp": current_xp,
                        "new_xp": new_xp,
                        "current_level": current_level,
                        "new_level": new_level,
                    }
                ]
                axiom.send_event(xp_data)

                if new_level > current_level:
                    await message.channel.send(f"{message.author.mention} You've leveled up to level {new_level}!")
                    await self.update_user_role_based_on_level(message, new_level)
                
                # Update the last message timestamp
                self.last_message_timestamps[(guild_id, user_id)] = current_time

    async def update_user_role_based_on_level(self, message, new_level):
        try:
            member = message.author
            if new_level in self.LEVEL_ROLE_MAP:
                new_role_id = self.LEVEL_ROLE_MAP[new_level]
                new_role = message.guild.get_role(new_role_id)

                if new_role:
                    # Remove old level roles
                    roles_to_remove = [
                        message.guild.get_role(rid)
                        for lvl, rid in self.LEVEL_ROLE_MAP.items()
                        if lvl != new_level
                    ]
                    await member.remove_roles(
                        *roles_to_remove, reason="Level up - updating roles"
                    )

                    # Add new role
                    await member.add_roles(new_role, reason="Level up")
                    await message.channel.send(
                        f"Congratulations {member.mention}, you have been promoted to {new_role.name}!"
                    )
                    data = [{
                        "type": "role",
                        "guild_id": str(message.guild.id),
                        "user_id": str(message.author.id),
                        "user_name": str(message.author.name),
                        "role_name": str(new_role.name),
                        "role_id": str(new_role.id),
                        "role_action": "add"
                    }]
                    axiom.send_event(data)
                else:
                    self.log_role_event(member, "role not found", new_level)
            else:
                # Log no new role assigned
                self.log_role_event(member, "no new role", new_level)
        except discord.Forbidden:
            await message.channel.send("I don't have permission to update roles.")
        except discord.HTTPException as e:
            await message.channel.send(f"An error occurred while updating roles: {e}")
        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {e}")

    def _level_for_xp(self, xp, base_xp=100, multiplier=0.8):
        level = 1
        while self._xp_for_level(level + 1, base_xp, multiplier) <= xp:
            level += 1
        return level

    def _xp_for_level(self, level, base_xp=100, multiplier=0.8):
        if level <= 1:
            return 0
        return int(base_xp * (level**multiplier))

    def _update_user_xp_and_level(self, guild_id, user_id, new_xp, new_level):
        guild_id_str = str(guild_id)
        user_id_str = str(user_id)
        current_time = datetime.datetime.now()

        with tracer.start_as_current_span(
            "update_user_xp_and_level", attributes={"type": "db"}
        ):
            with tracer.start_as_current_span("update_user_xp_and_level_query"):
                query = """
                INSERT INTO user_xp (guild_id, user_id, xp, level, last_updated)
                VALUES (%s, %s, %s, %s, %s)
                USING TTL 604800
                """
                self.session.execute(
                    query, [guild_id_str, user_id_str, new_xp, new_level, current_time]
                )

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
                        # Initialize new user with Level 1 and 0 XP
                        self._update_user_xp_and_level(guild_id, user_id, 0, 1)
                        return 0, 1
                return row.xp, row.level

    def log_role_event(self, member, action, level):
        data = {
            "type": "role",
            "guild_id": str(member.guild.id),
            "user_id": str(member.id),
            "user_name": str(member.name),
            "role_action": action,
            "level": level
        }
        axiom.send_event([data])