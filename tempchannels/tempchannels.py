from redbot.core import Config, commands
from redbot.core.bot import Red
from dislash import *
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Kitbash:6j68WjZGI3Nmvw8Q@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = client.FortniteITA
coll = db["temp-channels"]

BaseCog = getattr(commands, "Cog", object)
 
class TempChannels(BaseCog):
  
  def __init__(self, bot, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bot = bot
      
  def cog_unload(self):
    self.bot.slash.teardown()

@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
    if before.channel != 709783766712713358 and after.channel == 709783766712713358:
        doc = coll.find_one({"_id": member.id})
        if doc:
            return await member.move_to(self.bot.get_channel(doc.channel))

        channel = await member.guild.create_voice_channel(member.nick)
        await member.move_to(channel)
        await doc.insert_one({"_id": member.id, "channel", channel.id})
        #add user to voice-commands

    if before.channel != None and after.channel == None:
        if before.channel.category_id == 998609976044027984:
            if len(before.channel.members) == 0:
                await channel.delete()

