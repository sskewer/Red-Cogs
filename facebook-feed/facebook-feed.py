import datetime
import threading
import discord
from discord.ext import tasks
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
  async def facebook(self, ctx, option, value = None):
    """Modificare alcuni valori nel database"""
    epicstaff = ctx.guild.get_role(454262403819896833)
    moderatori = ctx.guild.get_role(454262524955852800)
    if epicstaff in ctx.author.roles or moderatori in ctx.author.roles:
      # Color
      if option == "color":
        if value.startswith("#"):
          # Aggiungere al database
          await ctx.message.add_reaction("✅")
        else:
          await ctx.message.add_reaction("🚫")
      # Avatar
      elif option == "avatar":
        if value == None:
          if ctx.message.attachments[0] != None:
            url = ctx.message.attachments[0].url
          else:
            await ctx.message.add_reaction("🚫")
        elif value.startswith("http"):
          url = value
        else:
          await ctx.message.add_reaction("🚫")
        # Aggiungere al database (url)
        await ctx.message.add_reaction("✅")
      # Default
      else:
        await ctx.message.add_reaction("🚫")
  
  #------------# FEED CHECKER #------------#
  
  @commands.Cog.listener()
  async def on_ready():
    """Controllare nuovi post dalla pagina Facebook e nel caso pubblicarli"""
    self.loop.start()
  
  @tasks.loop(minutes=5)
  async def loop(self):
    post = next(get_posts('FortniteGameITALIA', pages=1))
    if post["text"] != None:
      # Prendere info dal database e creare l'embed
        
