import asyncio
import datetime
import discord

from redbot.core import commands
from twitter_scraper import get_tweets
from translate import Translator

BaseCog = getattr(commands, "Cog", object)

class FnStatus(BaseCog):
    """Inviare tweet tradotti in italiano degli account Twitter di Fortnite"""
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator(to_lang="it")
        
        # self.translator.translate("This is a pen.")
        
        
        #for tweet in get_tweets('FortniteStatus', pages=1):
        #print(tweet['text'])
        
    
