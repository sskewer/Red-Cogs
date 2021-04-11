import datetime
import discord

from redbot.core import Config, commands
from redbot.core.bot import Red


BaseCog = getattr(commands, "Cog", object)

class DatabaseSharing(BaseCog):
    
    def __init__(self, bot):
        self.bot = bot
        self.epiclink = bot.get_cog("EpicLinking")
