import discord
import yaml

from contextlib import suppress
from redbot.core.commands import commands
from redbot.core import checks
from dislash import *
from yaml.scanner import ScannerError


CUSTOM_ID_PREFIX = "btnroles:"

def get_custom_id(role_id: str):
    return f"{CUSTOM_ID_PREFIX}{role_id}"

  
BaseCog = getattr(commands, "Cog", object)

class NitroBoosters(BaseCog):
  """Gestire i ruoli dei colori dei Nitro Booster"""
  
  def __init__(self, bot, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bot = bot

  def cog_unload(self):
    self.bot.slash.teardown()
    
  @commands.command()
  @checks.admin_or_permissions(manage_roles=True)
  async def setcolors(self, ctx, *, message: str):
    
    if not ctx.message.attachments:
      return await ctx.send("Devi **allegare** un file YAML!", delete_after=20.0)

    attachment: discord.Attachment = ctx.message.attachments[0]
    if not attachment.filename.lower().endswith((".yaml", ".yml")):
      return await ctx.send("Solo **file YAML** sono supportati!", delete_after=20.0)

    try:
      yaml_file = yaml.safe_load(await attachment.read())
    except yaml.scanner.ScannerError as e:
      return await ctx.send(f"**File YAML non valido**\n{e.problem_mark}")

    btns = []
    for label, config in yaml_file.items():
      b = Button(
        label=label,
        emoji=config.get("emoji"),
        custom_id=get_custom_id(config.get("role_id")),
        style=config.get("style", 1))
      btns.append(b)
        
    chunked_btns = []
    chunk_size = 5
    for i in range(0, len(btns), chunk_size):
      chunked_btns.append(btns[i:i+chunk_size])

    components = []
    for chunk in chunked_btns:
      components.append(ActionRow(*chunk))
      
    await ctx.send(message, components=components)
    
    
  @commands.Cog.listener()
  async def on_button_click(self, inter):
    button_id = inter.component.custom_id
    if not button_id.startswith(CUSTOM_ID_PREFIX):
      return

    button_id = button_id.replace(CUSTOM_ID_PREFIX, "")

    role = inter.guild.get_role(int(button_id))
    if not role:
      return await inter.reply(f"***Ops... qualcosa è andato storto!***", ephemeral=True, delete_after=20.0)

    if role.id in [r.id for r in inter.author.roles]:
      await inter.author.remove_roles(role)
      return await inter.reply(f"🙃 Ti ho rimosso il colore `{inter.component.label}`!", ephemeral=True, delete_after=20.0)
    
    role_ids = []
    msg = await inter.channel.fetch_message(inter.message.id)
    for component in msg.components:
      for button in component.to_dict().get("components"):
        role_ids.append(int(button.get("custom_id").replace(CUSTOM_ID_PREFIX, "")))
    
    for role_id in role_ids:
      to_remove = inter.guild.get_role(role_id)
      if to_remove.id is not int(button_id) and to_remove.id in [r.id for r in inter.author.roles]:
        try:
          await inter.author.remove_roles(to_remove)
        except:
          pass
        
    await inter.author.add_roles(role)
    await inter.reply(f"👉 Ti ho aggiunto il colore `{inter.component.label}`!", ephemeral=True, delete_after=20.0)
    
    
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    nitro_role = discord.utils.get(after.guild.roles, name="Nitro Booster")
    channel = discord.utils.get((await after.guild.fetch_channels()), name="cambia-colore")
    msg = await channel.fetch_message(channel.last_message_id)
    
    if msg is None:
      return

    if nitro_role in before.roles and nitro_role not in after.roles:
      color_ids = []
      for component in msg.components:
        for button in component.to_dict().get("components"):
          color_ids.append(int(button.get("custom_id").replace(CUSTOM_ID_PREFIX, "")))
        
      for color_id in color_ids:
        color = after.guild.get_role(color_id)
        if color.id in [r.id for r in after.roles]:
          try:
            await after.remove_roles(color)
          except:
            pass
