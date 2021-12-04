import discord
from contextlib import suppress
from redbot.core import commands


#----------------# SETUP #----------------#

nitro_id = 613774322179375105
colors_id = [778163336910471168, 778164006971113473, 778181408128237628, 778164137184329748, 778164311503667200, 778164647584464896, 778163064364990505, 778164449738489877, 778161810653839360]

#-----------------------------------------#


BaseCog = getattr(commands, "Cog", object)

class NitroBoosters(BaseCog):
  """Gestire i ruoli dei colori dei Nitro Booster"""
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    
