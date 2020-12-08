import datetime
import threading
import discord
from discord.ext import tasks
from contextlib import suppress
from redbot.core import Config, commands
from redbot.core.data_manager import cog_data_path
from facebook_scraper import get_posts

BaseCog = getattr(commands, "Cog", object)

class FacebookFeed(BaseCog):
  """Pubblicare i post di una pagina Facebook in un canale"""
  
  def __init__(self, bot):
    self.bot = bot    
    self.config = Config.get_conf(self, identifier=4000121111111111, force_registration=True)
    default_global = {}
    default_guild = {"color": "#fadb89", "avatar": "https://i.postimg.cc/W3XV58CH/Facebook-Icon.png", "last_feed": 1}
    self.config.register_global(**default_global)
    self.config.register_guild(**default_guild)
  
  #--------------# COMMANDS #--------------#
  
  @commands.guild_only()
  @commands.command(aliases = ["fb"])
  async def facebook(self, ctx, option, value = None):
    """Modificare alcuni valori nel database"""
    epicstaff = ctx.guild.get_role(454262403819896833)
    moderatori = ctx.guild.get_role(454262524955852800)
    if epicstaff in ctx.author.roles or moderatori in ctx.author.roles:
      # Color
      if option == "color":
        if value.startswith("#"):
          await self.config.guild(ctx.guild).color.set(value)
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
        if url != None:
          await self.config.guild(ctx.guild).avatar.set(url)
          await ctx.message.add_reaction("✅")
      # Default
      else:
        await ctx.message.add_reaction("🚫")
  
  #------------# FEED CHECKER #------------#
  
  @commands.Cog.listener()
  async def on_message(self, message):
    """Controllare nuovi post dalla pagina Facebook e nel caso pubblicarli"""
    #self.loop.start()
  
  #@tasks.loop(seconds = 30)
  #async def loop():
    if message.author.id == 422746977772765184:
      post = next(get_posts('FortniteGameITALIA', pages=1))
      guild = self.bot.get_guild(454261607799717888)
      last_feed = await self.config.guild(guild).last_feed()
      if last_feed != None and last_feed != post["post_id"]:
        if post["text"] != None:
          color = await self.config.guild(guild).color()
          avatar = await self.config.guild(guild).avatar()
          if post["post_url"] != None:
            post_url = post["post_url"]
          else:
            post_url = "https://www.facebook.com/FortniteGameITALIA/"
          if post["time"] != None:
            ts = post["time"]
          else:
            ts = datetime.datetime.utcnow()
          hex_int = int(color.replace("#", "0x"), 16)
          embed = discord.Embed(colour = hex_int, description = post["text"], timestamp = ts)
          embed.set_author(name = "Fortnite (@FortniteGameITALIA)", icon_url = avatar, url = post_url)
          embed.set_footer(text = "Facebook", icon_url = "https://i.postimg.cc/W3XV58CH/Facebook-Icon.png")
          if post["image"] != None:
            embed.set_image(url = post["image"])
          msg = await self.bot.get_channel(454264582622412801).send(embed=embed)
          await self.config.guild(guild).last_feed.set(post["post_id"])
          try:
            await msg.publish()
          except:
            pass
