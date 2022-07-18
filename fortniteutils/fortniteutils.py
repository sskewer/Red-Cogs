import re
import dislash
import discord
import asyncio
import datetime
import fortnite_api

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
allowed_channel = 702576186185875546
fn_api_icon = "https://fortnite-api.com/assets/img/logo_small.png"


BaseCog = getattr(commands, "Cog", object)
 
class FortniteUtils(BaseCog):
  
  def __init__(self, bot, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bot = bot
      
  def cog_unload(self):
    self.bot.slash.teardown()
    

  #---------------------------# PowerLevel #---------------------------# 
  
  @dislash.guild_only()
  @slash_command(description="Gestisce il livello di Potenza STW all'interno del server")
  async def powerlevel(self, inter):
      pass
    
  @powerlevel.sub_command(
    description="Aggiunge il livello di Potenza STW al proprio nickname",
    options=[
        Option("level", "Inserisci il livello di Potenza STW", OptionType.INTEGER, required=True)
    ]
  )
  async def set(self, inter, level=None):
    if int(inter.channel.id) != int(allowed_channel):
      return await inter.reply(f"🤐 Spostati in <#{allowed_channel}> per usare questo comando!", ephemeral=True)
    # Vars
    index = int(level)
    member = inter.guild.get_member(inter.author.id)
    # Level Check
    if index < 1 or index > max_level:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto: **livello non valido**!", ephemeral=True)
    # New Nickname
    new_nick = getNick(inter.author.display_name) + " [⚡" + str(index) + "]"
    if len(new_nick) > 32:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto: **massimo dei caratteri superato**!", ephemeral=True)
    # Set Nickname
    try:
      await member.edit(nick=new_nick)
    except:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto: **permessi insufficienti**!", ephemeral=True)
    await inter.reply(f"👉 Ho **aggiunto** il livello al tuo nickname!", ephemeral=True)
  
  @powerlevel.sub_command(description="Rimuove il livello di Potenza STW dal proprio nickname")
  async def reset(self, inter):
    if int(inter.channel.id) != int(allowed_channel):
      return await inter.reply(f"🤐 Spostati in <#{allowed_channel}> per usare questo comando!", ephemeral=True)
    member = inter.guild.get_member(inter.author.id)
    # New Nickname
    original_nick = getNick(inter.author.display_name)
    if original_nick is inter.author.display_name:
      return await inter.reply(f"😕 Sembra che non ci sia **nessun livello** nel tuo nickname!", ephemeral=True)
    # Reset Nickname
    try:
      await member.edit(nick=original_nick)
    except:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto: **permessi insufficienti**!", ephemeral=True)
    await inter.reply(f"🙃 Ho **rimosso** il livello dal tuo nickname!", ephemeral=True)
    
    
  #---------------------------# Fortnite Map #---------------------------# 

  @dislash.guild_only()
  @slash_command(
    description="Restituisce la mappa attuale di Fortnite Battaglia Reale",
    options=[
        Option("pois", "Aggiunge o rimuove i punti di interesse sulla mappa", OptionType.BOOLEAN, required=False)
    ]
  )
  async def map(self, inter, pois=None):
    pois = False if pois is False else True
    if int(inter.channel.id) != int(allowed_channel):
      return await inter.reply(f"🤐 Spostati in <#{allowed_channel}> per usare questo comando!", ephemeral=True)
    # FortniteAPI
    fn_api = fortnite_api.FortniteAPI(api_key=(await self.bot.get_shared_api_tokens('FortniteAPI'))['api_key'], run_async=True)
    # Getting Data
    try:
      map = await fn_api.map.fetch(language=fortnite_api.GameLanguage.ITALIAN)
    except:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto!", ephemeral=True)
    # Map URL
    url = map.poi_image if pois is True else map.blank_image
    if url is None:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto!", ephemeral=True)
    # Response
    embed = discord.Embed(timestamp=datetime.datetime.utcnow())
    embed.set_image(url=url)
    embed.set_footer(text="Creato con ❤️ • Fortnite IT", icon_url=fn_api_icon)
    await inter.reply(embed=embed, ephemeral=False)

    
  #---------------------------# Fortnite Map #---------------------------# 

  @dislash.guild_only()
  @slash_command(
    description="Restituisce la notizie giornaliere di Fortnite",
    options=[
        Option(
            "gamemode",
            description="Seleziona la modalità tra quelle disponibili",
            type=OptionType.STRING,
            required=True,
            choices=[
                OptionChoice("Battaglia Reale", "br"),
                OptionChoice("Creativa", "cr"),
                OptionChoice("Salva il Mondo", "stw"),
            ],
        )
    ]
  )
  async def news(self, inter, gamemode: str):
    #if int(inter.channel.id) != int(allowed_channel):
    #  return await inter.reply(f"🤐 Spostati in <#{allowed_channel}> per usare questo comando!", ephemeral=True)
    # FortniteAPI
    fn_api = fortnite_api.FortniteAPI(api_key=(await self.bot.get_shared_api_tokens('FortniteAPI'))['api_key'], run_async=True)
    # Getting Data
    try:
      if gamemode == "stw":
        news_type = fortnite_api.NewsType.SAVE_THE_WORLD
        title = "Salva il Mondo"
        icon = "https://cdn.discordapp.com/emojis/775676864055214080.png"
      elif gamemode == "cr":
        news_type = fortnite_api.NewsType.CREATIVE
        title = "Creativa"
        icon = "https://cdn.discordapp.com/emojis/775676864664305674.png"
      else:
        news_type = fortnite_api.NewsType.BATTLE_ROYALE
        title = "Battaglia Reale"
        icon = "https://cdn.discordapp.com/emojis/775676863976046592.png"
      news = await fn_api.news.fetch_by_type(news_type=news_type, language=fortnite_api.GameLanguage.ITALIAN)
    except:
      return await inter.reply(f"😕 Ops... qualcosa è andato storto!", ephemeral=True)
    # News Data
    date = news.date if news.date is not None else datetime.datetime.utcnow()
    if news.image is None and gamemode != "stw":
      return await inter.reply(f"😕 Sembra che **non ci siano notizie** da questa modalità!", ephemeral=True)
    # Save the World
    if gamemode == "stw":
      #try:
      index = 1
      pages = []
      for msg in news.messages:
        page = discord.Embed(title=f"{msg.title} ({str(index)}/{str(len(news.messages))})", description=msg.body", timestamp=date)
        page.set_image(url=msg.image_url)
        page.set_author(name=title, icon_url=icon)
        page.set_footer(text="Notizie aggiornate a 🕓", icon_url=fn_api_icon)
        pages.append(page)
        index++
      row = ActionRow(
        Button(
          style = ButtonStyle.grey,
          emoji = "◀️",
          custom_id = f"menu_{str(inter.author.id)}_previous"
        ),
        Button(
          style = ButtonStyle.grey,
          emoji = "▶️",
          custom_id = f"menu_{str(inter.author.id)}_next"
        ),
        Button(
          style = ButtonStyle.grey,
          emoji = "🛑",
          custom_id = f"menu_{str(inter.author.id)}_close"
        )
      )
      index = 1
      menu = await inter.reply(embed=pages[index-1], components=[row], ephemeral=False)
      on_click = menu.create_click_listener(timeout=60)

      @on_click.not_from_user(inter.author, cancel_others=True, reset_timeout=False)
      async def on_wrong_user(click):
        await click.reply(f"🤐 Solo **{str(inter.author.display_name)}** può interagire con questi pulsanti!", ephemeral=True)

      @on_click.matching_id(f"menu_{str(inter.author.id)}_previous")
      async def on_previous_button(click):
        index = index - 1
        await menu.edit(embed=pages[index-1])

      @on_click.matching_id(f"menu_{str(inter.author.id)}_next")
      async def on_next_button(click):
        index = index + 1
        await menu.edit(embed=pages[index-1])

      @on_click.matching_id(f"menu_{str(inter.author.id)}_close")
      async def on_close_button(click):
        await menu.edit(components=[])

      @on_click.timeout
      async def on_timeoutclick():
        await menu.edit(components=[])
      #except:
        #return await inter.reply(f"😕 Ops... qualcosa è andato storto!", ephemeral=True)
    # Battle Royale & Creative
    embed = discord.Embed(timestamp=date)
    embed.set_image(url=news.image)
    embed.set_author(name=title, icon_url=icon)
    embed.set_footer(text="Notizie aggiornate a 🕓", icon_url=fn_api_icon)
    await inter.reply(embed=embed, ephemeral=False)
