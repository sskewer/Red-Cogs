import asyncio
import datetime
import discord

from discord.ext import tasks
from redbot.core import Config, commands
from twitter_scraper import get_tweets
from translate import Translator

BaseCog = getattr(commands, "Cog", object)

class FnStatus(BaseCog):
    """Inviare tweet tradotti in italiano degli account Twitter di Fortnite"""
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator(to_lang="it")
        self.config = Config.get_conf(self, identifier=4000121212121212, force_registration=True)
        default_guild = {"last_feed": None}
        self.config.register_guild(**default_guild)
        self.checker.start()
        
    def cog_unload(self):
        self.checker.cancel()
        
    @tasks.loop(minutes=10, reconnect=True)
    async def checker(self):
        guild = self.bot.get_guild(454261607799717888)
        last_feed = await self.config.guild(guild).last_feed() 
                                  
    @checker.before_loop
    async def before_checker(self):
        await self.bot.wait_until_ready()
        
        # self.translator.translate("This is a pen.")
        
        
        #for tweet in get_tweets('FortniteStatus', pages=1):
        #print(tweet['text'])
        
    
