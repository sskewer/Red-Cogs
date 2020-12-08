import datetime
import discord
from discord.ext import tasks
from contextlib import suppress
from redbot.core import commands
#from pymongo import MongoClient
from facebook_scraper import get_posts

cluster = MongoClient("mongodb://modmail:dbFortniteITA@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = cluster["FortniteITA"]
collection = db["Facebook"]

BaseCog = getattr(commands, "Cog", object)

class FacebookFeed(BaseCog):
  """Pubblicare i post di una pagina Facebook in un canale"""
  
  def __init__(self, bot):
    self.bot = bot
    self.path = str(cog_data_path(self)).replace("\\", "/")
    self.config = Config.get_conf(self, identifier=4000121111111111, force_registration=True)
    default_settings = {"color": None, "avatar": None, "last_feed": 1}
    self.config.register_guild(**default_settings)
  
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
          #try:
          #collection.update_one({"_id" : "setup"}, {"$set" : {"color" : value}})
          await ctx.message.add_reaction("✅")
          #except:
            #await ctx.message.add_reaction("🚫")
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
          #try:
          #collection.update_one({"_id" : "setup"}, {"$set" : {"avatar" : url}})
          await ctx.message.add_reaction("✅")
          #except:
            #await ctx.message.add_reaction("🚫")
      # Default
      else:
        await ctx.message.add_reaction("🚫")
  
  #------------# FEED CHECKER #------------#
  
  @commands.Cog.listener()
  async def on_ready():
    """Controllare nuovi post dalla pagina Facebook e nel caso pubblicarli"""
    self.loop.start()
  
  @tasks.loop(minutes = 5)
  async def loop(self):
    post = next(get_posts('FortniteGameITALIA', pages=1))
    last_feed = collection.find_one({"_id" : "feed"})["last"]
    if last_feed != None and last_feed != post["post_id"]:
      if post["text"] != None:
        setup = collection.find_one({"_id" : "setup"})
        if setup != None:
          color = setup["color"]
          avatar = setup["avatar"]
          if color != None and avatar != None:
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
            collection.update_one({"_id" : "feed"}, {"$set" : {"last" : post["post_id"]}})
            try:
              await msg.publish()
            except:
              pass
