from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core import Config
from dislash import *

#---------# SETUP #---------#

target_guild = 454261607799717888
main_channel = 709783766712713358
main_category = 998609976044027984
commands_channel = 998609829230813236

BaseCog = getattr(commands, "Cog", object)
 
class TempChannels(BaseCog):
  
  def __init__(self, bot, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bot = bot
    self.config = Config.get_conf(self, identifier=4900121111222111, force_registration=True)
    default_member = {"channel": None}
    self.config.register_member(**default_member)
      
  def cog_unload(self):
    self.bot.slash.teardown()

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    if member.guild.id != target_guild or member.bot is True:
      return
    if before.channel is not None and before.channel.id == main_channel and after.channel is not None and after.channel.category_id == main_category:
      return
    
    # Channel Creation
    if (before.channel is None or before.channel.id != main_channel) and after.channel.id == main_channel:
      user_channel = await self.config.member(member).channel()
      # Existing User Channel
      if user_channel is not None:
        return await member.move_to(self.bot.get_channel(user_channel))
      # Non-Existing User Channel
      channel = await member.guild.create_voice_channel(name=member.display_name, topic=f"👤 **Proprietario: {member.mention}**", user_limit=4, category=self.bot.get_channel(main_category))
      await member.move_to(channel)
      await self.config.member(member).channel.set(channel.id)
      return await self.bot.get_channel(commands_channel).set_permissions(member, view_channel=True, read_messages=True, read_message_history=True, send_messages=True, use_slash_commands=True)
      
    # Channel Elimination
    if before.channel is not None and before.channel.category_id == main_category:
      if len(before.channel.members) < 1:
        try:
          owner = before.channel.guild.get_member(before.channel.name[21:-3])
        except:
          owner = None
        if owner is not None:
          await self.config.member(owner).channel.set(None)
          await self.bot.get_channel(commands_channel).set_permissions(member, overwrite=None)
        return await before.channel.delete()

