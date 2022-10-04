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
  
  @deletedmsg.sub_command(description="Visualizza le impostazioni attuali per i log")
  async def settings(self, inter):
    ch = await self.config.guild(inter.guild).channel()
    toggle = await self.config.guild(inter.guild).enabled()
    color = discord.Color.green() if toogle is True else discord.Color.red()
    status = "Enabled" if toogle is True else "Disabled"
    embed = discord.Embed(color = color, title = "Log Settings for Deleted Messages", timestamp = datetime.datetime.utcnow())
    embed.add_field(name = "Channel", value = f"<#{str(ch)}> **| `{str(ch)}`**", inline = True)
    embed.add_field(name = "Status", value = status, inline = True)
    embed.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
    await inter.reply(embed=embed, ephemeral=False)
  
  @deletedmsg.sub_command(
    description="Imposta il canale di invio dei log",
    options=[
        Option("channel", "Specifica il canale in cui inviare i log", OptionType.CHANNEL, required=True)
    ]
  )
  async def setchannel(self, inter, channel):
    if channel.type not in ["text", "news", "forum"]:
      return await inter.reply(f"🤐 Questo canale **non può essere utilizzato** per i log!", ephemeral=True)
    try:
      await self.config.guild(inter.guild).channel.set(channel.id)
      await inter.reply(f"📨 <#{str(channel.id)}> sarà utilizzato per **inviare i log** dei messaggi eliminati!", ephemeral=False)
    except:
      await inter.reply(f"💢 Ops... **qualcosa non ha funzionato**: riprova più tardi!", ephemeral=True)
  
  @deletedmsg.sub_command(
    description="Attiva o disattiva l'invio dei log",
    options=[
        Option(
            "switch",
            description="Scegli lo stato dell'invio dei log",
            type=OptionType.STRING,
            required=True,
            choices=[
                OptionChoice("ON", "on"),
                OptionChoice("OFF", "off"),
            ],
        )
    ]
  )
  async def status(self, inter, switch: str):
    current = await self.config.guild(inter.guild).enabled()
    if switch == "on":
      if current is True:
        return await inter.reply(f"🤐 L'invio automatico di messaggi è **già abilitato**!", ephemeral=True)
      else:
        try:
          await self.config.guild(inter.guild).enabled.set(True)
          await inter.reply(f"✅ L'invio automatico di messaggi è **ora abilitato**!", ephemeral=False)
        except:
          await inter.reply(f"💢 Ops... **qualcosa non ha funzionato**: riprova più tardi!", ephemeral=True)
    else:
      if current is False:
        return await inter.reply(f"🤐 L'invio automatico di messaggi è **già disabilitato**!", ephemeral=True)
      else:
        try:
          await self.config.guild(inter.guild).enabled.set(False)
          await inter.reply(f"⛔ L'invio automatico di messaggi è **ora disabilitato**!", ephemeral=False)
        except:
          await inter.reply(f"💢 Ops... **qualcosa non ha funzionato**: riprova più tardi!", ephemeral=True)
    
    
  #-------------------------------------------------------#
    
  @commands.Cog.listener()
  async def on_raw_message_delete(self, payload : discord.RawMessageDeleteEvent):
    
