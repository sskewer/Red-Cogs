import asyncio

from contextlib import suppress
import discord
from redbot.core import commands

######### CONFIG #########
role = id
reaction = name
message = id
welcome_channel = id
welcome_message = string
##########################

BaseCog = getattr(commands, "Cog", object)

class WelcomeRoleReaction(BaseCog):
    """Bind a role reaction to a message and give the welcome to a specific channel"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user)