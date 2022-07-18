from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core import Config
from dislash import *

BaseCog = getattr(commands, "Cog", object)
 
class TempChannels(BaseCog):
  
  def __init__(self, bot, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bot = bot
    self.config = Config.get_conf(self, identifier=4900121111222111, force_registration=True)
    default_member = {"channel": 773849790844239872}
    self.config.register_member(**default_member)
      
  def cog_unload(self):
    self.bot.slash.teardown()

@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
    if before.channel != 709783766712713358 and after.channel == 709783766712713358:
        doc = await self.config.member(member).channel()
        if doc:
            return await member.move_to(self.bot.get_channel(doc.channel))

        channel = await member.guild.create_voice_channel(member.nick)
        await member.move_to(channel)
        await self.config.member(member).value_name.set(channel.id)
        #add user to voice-commands

    if before.channel != None and after.channel == None:
        if before.channel.category_id == 998609976044027984:
            if len(before.channel.members) == 0:
                await channel.delete()

