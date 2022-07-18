import re
import discord

from redbot.core import Config, commands
from redbot.core.bot import Red
from dislash import *


def getNick(nick:str):
  form_nick = re.sub(r'\s+\[⚡\d+\]', '', nick)
  if form_nick:
    return form_nick
  else:
    return None

# Setup
max_level = 138
allowed_channels = [702576186185875546]


BaseCog = getattr(commands, "Cog", object)
 
class PowerLevel(BaseCog):
  
  def __init__(self, bot, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def cog_unload(self):
    self.bot.slash.teardown()

  @dislash.guild_only()
  @slash_command(description="Gestisce il PowerLevel all'interno del server")
  async def powerlevel(self, inter):
      pass
    
    
  @powerlevel.sub_command(
    description="Aggiunge il livello al proprio nickname",
    options=[
        Option("level", "Inserisci il livello", OptionType.INTEGER)
    ]
  )
  async def set(self, inter, level=None):
    # Vars
    index = int(level)
    member = inter.guild.get_member(inter.author.id)
    # Level Check
    if index < 1 or index > max_level:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto: **livello non valido**!", ephemeral=True)
    tag = " [⚡" + str(index) + "]"
    # New Nickname
    new_nick = getNick(inter.author.display_name) + " [⚡" + str(index) + "]"
    if len(new_nick) > 32:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto: **massimo dei caratteri superato**!", ephemeral=True)
    # Set Nickname
    await member.edit(nick=new_nick)
    await inter.reply(f"👉 Ho **aggiunto** il livello al tuo nickname!", ephemeral=True)
  
  
  @powerlevel.sub_command(description="Rimuove il livello dal proprio nickname")
  async def reset(self, inter):
    if inter.channel.id not in allowed_channels:
      return
    member = inter.guild.get_member(inter.author.id)
    # New Nickname
    original_nick = getNick(inter.author.display_name)
    await member.edit(nick=original_nick)
    # Response
    await inter.reply(f"🙃 Ho **rimosso** il livello dal tuo nickname!", ephemeral=True)
