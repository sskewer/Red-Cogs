import json
import asyncio
import discord
import random

from redbot.core import commands
from redbot.core.data_manager import bundled_data_path
    
BaseCog = getattr(commands, "Cog", object)

class RandomNick(BaseCog):
    """Pick a random nickname and set it for the user"""
    def __init__(self, bot):
        self.bot = bot
        with open(f'{bundled_data_path(self)}/nicknames.json') as f:
            self.nick_name_list = json.load(f)

    @commands.guild_only()
    @commands.command(aliases=["random"])
    @commands.has_permissions(manage_nicknames=True)
    async def randomnick(self, ctx, *, user: discord.Member):
        randomnick = random.choice(self.nick_name_list)
        try:
            await user.edit(nick=randomnick)
            await ctx.send(f":crayon: Il nuovo nome generato casualmente per **{user.name}** è **{randomnick}**.")
        except:
            await ctx.send(f":crayon: Non riesco a generare casualmente un soprannome per **{user.name}**.")
