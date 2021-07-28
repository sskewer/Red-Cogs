import discord
from uuid import uuid4
from redbot.core import commands
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Kitbash:6j68WjZGI3Nmvw8Q@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = client.FortniteITA

BaseCog = getattr(commands, "Cog", object)

class VoteSystem(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
    self.mongo = db["vote-system"]
    self.vote_config = {
      "url": "https://docs.google.com/forms/d/e/1FAIpQLSc_cZEdmgq23IR8_m6YjbVZTCeCqz2aS8zJ1nrLBWPL0vsmhQ/viewform?usp=pp_url&entry.1831324353={0}",
      "guild": 454261607799717888,
      "channel": 454268474534133762,
      "message": 869894908767502356
    }
    print("1")
      
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
    print("2")
    # Token Generation
    token = uuid4()
    # Variables
    guild = self.bot.get_guild(self.vote_config["guild"])
    channel = guild.get_channel(self.vote_config["channel"])
    message = await channel.fetch_message(self.vote_config["message"])
    # Token Check
    token_list = self.mongo.find({})
    while len([x for x in token_list if x.token == token]) > 0:
      token = uuid4()
    # User Check
    user_check = self.mongo.find({ "guild": guild.id, "user": payload.member.id })
    # Script
    if len(user_check) == 0 and payload.member.bot == False and payload.channel_id == channel.id and payload.message_id == message.id and str(payload.emoji) == "✅":
      # Database Update
      self.mongo.insert_one({ "guild": str(guild.id), "user": str(payload.member.id), "token": str(token) })
      link = self.vote_config["url"].format(token)
      # Send DM
      await channel.send(link)

def setup(bot):
  bot.add_cog(VoteSystem(bot))
