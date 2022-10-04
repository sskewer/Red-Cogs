import discord
import yaml

from redbot.core.commands import commands
from redbot.core import Config, checks

from contextlib import suppress
from dislash import *

  
BaseCog = getattr(commands, "Cog", object)

class DeletedMsg(BaseCog):
  """Log per i messaggi eliminati in un server"""
  
  def __init__(self, bot, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bot = bot
    self.config = Config.get_conf(self, identifier=4000121212121335, force_registration=True)
    default_guild = {"channel": None, "enabled": False}
    self.config.register_guild(**default_guild)

  def cog_unload(self):
    self.bot.slash.teardown()
    
  #-------------------------------------------------------#
  
  @dislash.guild_only()
  @dislash.has_permissions(manage_sever=True)
  @slash_command(description="Impostazioni dei log dei messaggi eliminati del server")
  async def deletedmsg(self, inter):
    pass
  
  @deletedmsg.sub_command(
    description="Imposta il canale di invio dei log",
    options=[
        Option("channel", "Specifica il canale in cui inviare i log", OptionType.CHANNEL, required=True)
    ]
  )
  async def setchannel(self, inter, channel):
  if channel.type not in ["text", "news", "forum"]:
    return await inter.reply(f"🤐 Questo canale **non può essere utilizzato** per i log!", ephemeral=True)
  await self.config.guild(inter.guild).channel.set(channel.id)
  
    
    
    
  #-------------------------------------------------------#
    
  @commands.Cog.listener()
  async def on_raw_message_delete(self, payload : discord.RawMessageDeleteEvent):
    
