import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class ChannelReminder(BaseCog):
  """Lasciare un reminder come ultimo messaggio del canale"""
  
  def __init__(self, bot: Red):
        self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
        
        #--------- Bug Traduzione ---------#
        if message.channel.id == 674689662509514752:
    
