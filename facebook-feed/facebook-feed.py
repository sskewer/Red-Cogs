import datetime
import threading
import discord
from contextlib import suppress
from redbot.core import commands
from facebook_scraper import get_posts

BaseCog = getattr(commands, "Cog", object)

class FacebookFeed(BaseCog):
  """Pubblicare i post di una pagina Facebook in un canale"""
  
  def __init__(self, bot):
    self.bot = bot
  
  #--------------# COMMANDS #--------------#
  
  @commands.guild_only()
  @commands.command(aliases=["fb"])
  async def facebook(self, ctx):
    """Modificare alcuni valori nel database"""
    args = ctx.message.content.replace("?facebook ", "").split()
    epicstaff = ctx.guild.get_role(454262403819896833)
    moderatori = ctx.guild.get_role(454262524955852800)
    if epicstaff in ctx.author.roles or moderatori in ctx.author.roles:
      if args[0] == "color":
        # Code
        await ctx.message.add_reaction("✅")
      elif args[0] == "avatar":
        # Code
        await ctx.message.add_reaction("✅")
      else:
        await ctx.message.add_reaction("🚫")
      # Cambiare il colore o il link immagine nel database
  
  #------------# FEED CHECKER #------------#
  
  @commands.Cog.listener()
  async def on_ready():
    """Controllare nuovi post dalla pagina Facebook e nel caso pubblicarli"""
    async def feed_func():
      post = next(get_posts('FortniteGameITALIA', pages=1))
      if post["text"] != None:
        # Prendere info dal database e creare l'embed
    feed_checker = threading.Timer(600, feed_func)
    feed_checker.start()
        
