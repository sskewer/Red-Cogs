import asyncio

from contextlib import suppress
import discord
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class LockServer(BaseCog):
    """Lock the server and block everyone to send messages"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["serverlock"])
    @checks.has_permissions("BAN_MEMBERS")
    async def lockserver(self, ctx):
        
    
