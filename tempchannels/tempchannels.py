from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core import Config
from dislash import *

#---------# SETUP #---------#

main_channel = 709783766712713358
main_category = 998609976044027984

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
    print(after.channel)
    if before.channel != main_channel and after.channel == main_channel:
      user_channel = await self.config.member(member).channel()
      # Existing User Channel
      if user_channel is not None:
        return await member.move_to(self.bot.get_channel(user_channel))
      # Non-Existing User Channel
      channel = await member.guild.create_voice_channel(name=member.display_name, user_limit=4, category=self.bot.get_channel(main_category))
      await member.move_to(channel)
      await self.config.member(member).channel.set(channel.id)
      #add user to voice-commands

    #if before.channel != None and after.channel == None:
      #if before.channel.category_id == main_category:
        #if len(before.channel.members) == 0:
          #await channel.delete()

