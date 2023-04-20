import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class TweetRepost(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    

def setup(bot):
  bot.add_cog(TweetRepost(bot))
