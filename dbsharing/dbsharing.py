import datetime
import discord

from redbot.core import Config, commands
from redbot.core.bot import Red


BaseCog = getattr(commands, "Cog", object)

class DatabaseSharing(BaseCog):
    """Cog created for local database sharing"""
    def __init__(self, bot):
        self.bot = bot
        self.epiclinking = bot.get_cog("EpicLinking")
        
        guild = self.bot.get_guild(454261607799717888)
        verified_user_id = await self.epiclinking.settings.guild(guild).verified_user_id()
        if str(ctx.message.author.id) in verified_user_id:
            epic_id = verified_user_id[str(ctx.message.author.id)]
