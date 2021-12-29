import asyncio
import datetime
import discord

from redbot.core import commands
from twitter_scraper import get_tweets

BaseCog = getattr(commands, "Cog", object)

class FnStatus(BaseCog):
    """Inviare tweet tradotti in italiano degli account Twitter di Fortnite"""
    def __init__(self, bot):
        self.bot = bot
        
    
