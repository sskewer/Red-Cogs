import datetime
import discord
from contextlib import suppress
from redbot.core import commands
from facebook_scraper import get_posts

BaseCog = getattr(commands, "Cog", object)

class FacebookFeed(BaseCog):
  """Pubblicare i post di una pagina Facebook in un canale"""
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.guild_only()
  @commands.command(aliases=["fb"])
  async def facebook(self, ctx):
    """Modificare alcuni valori nel database"""
    args = ctx.message.content.replace("?facebook ", "")
    epicstaff = ctx.guild.get_role(454262403819896833)
    moderatori = ctx.guild.get_role(454262524955852800)
    if epicstaff in ctx.author.roles or moderatori in ctx.author.roles:
        # Cambiare il colore o il link immagine nel database
        
