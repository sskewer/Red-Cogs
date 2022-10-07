import discord
import dislash
import datetime

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
  @dislash.has_permissions(manage_guild=True)
  @slash_command(description="Impostazioni dei log dei messaggi eliminati del server")
  async def deletedmsg(self, inter):
    pass
  
  @deletedmsg.sub_command(description="Visualizza le impostazioni attuali per i log")
  async def settings(self, inter):
    ch = await self.config.guild(inter.guild).channel()
    toggle = await self.config.guild(inter.guild).enabled()
    channel = f"<#{str(ch)}> **| `{str(ch)}`**" if ch is not None else "Not setted"
    color = discord.Color.green() if toggle is True else discord.Color.red()
    status = "Enabled" if toggle is True else "Disabled"
    embed = discord.Embed(color = color, title = "Log Settings for Deleted Messages", timestamp = datetime.datetime.utcnow())
    embed.add_field(name = "Channel", value = channel, inline = True)
    embed.add_field(name = "Status", value = status, inline = True)
    embed.set_footer(text = inter.guild.name, icon_url = inter.guild.icon_url)
    await inter.reply(embed=embed, ephemeral=False)
  
  @deletedmsg.sub_command(
    description="Imposta il canale di invio dei log",
    options=[
        Option("channel", "Specifica il canale in cui inviare i log", OptionType.CHANNEL, required=True)
    ]
  )
  async def channel(self, inter, channel):
    if channel.type.name not in ["text", "news", "forum"]:
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
    if payload.guild_id is None:
      return
    guild = await self.bot.fetch_guild(payload.guild_id)
    if guild is None:
      return
    ch = await self.config.guild(guild).channel()
    toggle = await self.config.guild(guild).enabled()
    if toggle is False:
      return
    guild_chs = await guild.fetch_channels()
    log_ch = next(filter(lambda c: c.id == int(ch), guild_chs), None)
    if log_ch is None:
      return
    msg = payload.cached_message if payload.cached_message is not None else None
    if msg is None:
      msg_ch = next(filter(lambda c: c.id == payload.channel_id, guild_chs), None)
      if msg_ch is None:
        return
      try:
        msg = await msg_ch.fetch_message(payload.message_id) # Ottimizzare
      except:
        return
    if msg.author.bot is True:
      return
    embed = discord.Embed(color = discord.Color.gold(), title = "Messaggio Eliminato", timestamp = datetime.datetime.utcnow())
    embed.add_field(name = "ID Messaggio", value = f"`{str(msg.id)}`", inline = True)
    embed.add_field(name = "Canale", value = f"<#{str(msg.id)}>", inline = True)
    embed.set_footer(text = inter.guild.name, icon_url = inter.guild.icon_url)
    await log_ch.send(embed=embed)
    
    
