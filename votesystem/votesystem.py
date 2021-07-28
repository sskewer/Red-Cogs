import discord
from uuid import uuid4
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class VoteSystem(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
    self.vote_config = {
      "url": "https://docs.google.com/forms/d/e/1FAIpQLSc_cZEdmgq23IR8_m6YjbVZTCeCqz2aS8zJ1nrLBWPL0vsmhQ/viewform?usp=pp_url&entry.1831324353={0}",
      "guild": 454261607799717888,
      "channel": 1234,
      "message": 1234
    }
      
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
    # Token Generation
    token = uuid4()
    # Variables
    guild = self.bot.get_guild(self.vote_config["guild"])
    channel = guild.get_channel(self.vote_config["channel"])
    message = await channel.fetch_message(self.vote_config["message"])
    # Database Check
    
    # Script
    if member.bot == False and payload.channel_id == channel.id and payload.message_id == message.id and str(payload.emoji) == "✅":
      link = self.vote_config["url"].format(token)
      # Inviare DM all'utente con il link al voto

def setup(bot):
  bot.add_cog(VoteSystem(bot))
