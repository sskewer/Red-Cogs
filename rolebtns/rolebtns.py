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
    
    yaml = [item for item in ctx.message.attachments if item.filename.lower().endswith((".yaml", ".yml"))]
    if len(yaml) < 1:
      return await ctx.send("Devi **allegare** un file YAML!", delete_after=20.0)
    attachment: discord.Attachment = yaml[0]
      
    images = [item for item in ctx.message.attachments if item.filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".tiff"))]
    file: discord.File = await images[0].to_file(use_cached=True)

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
    
    if file is None:
      await ctx.send(message, components=components)
    else:
      await ctx.send(message, file=file, components=components)
    
  #-------------------------------------------------------#
    
  @commands.Cog.listener()
  async def on_button_click(self, inter):
    
    button_id = inter.component.custom_id
    if not button_id.startswith(CUSTOM_ID_PREFIX):
      return

    button_id = button_id.replace(CUSTOM_ID_PREFIX, "")

    role = inter.guild.get_role(int(button_id))
    if not role:
      return await inter.reply(f"***Ops... qualcosa è andato storto!***", ephemeral=True)

    if role.id in [r.id for r in inter.author.roles]:
      await inter.author.remove_roles(role)
      return await inter.reply(f"🙃 Ti ho rimosso il ruolo `{inter.component.label}`!", ephemeral=True)
        
    await inter.author.add_roles(role)
    await inter.reply(f"👉 Ti ho aggiunto il ruolo `{inter.component.label}`!", ephemeral=True)
