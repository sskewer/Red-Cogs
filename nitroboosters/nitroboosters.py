import discord
from contextlib import suppress
from redbot.core import commands


#----------------# SETUP #----------------#

channel_id = 778165263928655882
message_id = 778180901678219266
nitro_id = 613774322179375105
colors_id = [778163336910471168, 778164006971113473, 778181408128237628, 778164137184329748, 778164311503667200, 778164647584464896, 778163064364990505, 778164449738489877, 778161810653839360]

#-----------------------------------------#


BaseCog = getattr(commands, "Cog", object)

class NitroBoosters(BaseCog):
  """Gestire i ruoli dei colori dei Nitro Booster"""
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    # Channel & Message Checks
    guild = self.bot.get_guild(payload.guild_id)
    if not guild:
      return
    if payload.channel_id != channel_id or payload.message_id != message_id:
      return
    # Member Checks
    member = guild.get_member(payload.user_id)
    nitro = guild.get_role(nitro_id)
    if nitro not in member.roles:
      return
    # Get Message
    channel = guild.get_channel(channel_id)
    msg = await channel.fetch_message(message_id)
    # Remove Reactions
    for reaction in msg.reactions:
      if reaction.emoji is not payload.emoji:
        try:
          await reaction.remove(member)
        except:
          pass 
      
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    # Vars
    role = before.guild.get_role(nitro_id)
    channel = before.guild.get_channel(channel_id)
    msg = await channel.fetch_message(message_id)
    # Remove Reactions
    for reaction in msg.reactions:
      try:
        await reaction.remove(after)
      except:
        pass 
    # Remove Color Roles
    if role in before.roles and role not in after.roles:
      for id in colors_id:
        color = before.guild.get_role(id)
        if color in before.roles:
          try:
            await after.remove_roles(color)
          except:
            pass
