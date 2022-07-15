import discord
import yaml

from contextlib import suppress
from redbot.core import Config
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
    self.config = Config.get_conf(self, identifier=4000121111111002, force_registration=True)
    default_guild = {"channelID": None, "messageID": None}
    self.config.register_guild(**default_guild)

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
      
    btnMessage = await ctx.send(message, components=components)
    
    await self.config.guild(ctx.guild).channelID.set(ctx.channel.id)
    await self.config.guild(ctx.guild).messageID.set(btnMessage.id)
    
    
  #-------------------------------------------------------#
    
  @commands.Cog.listener()
  async def on_button_click(self, inter):
        
    messageID = await self.config.guild(inter.guild).messageID()
    
    if messageID is None or messageID is not inter.message.id:
      return
    
    button_id = inter.component.custom_id
    if not button_id.startswith(CUSTOM_ID_PREFIX):
      return

    button_id = button_id.replace(CUSTOM_ID_PREFIX, "")

    role = inter.guild.get_role(int(button_id))
    if not role:
      return await inter.reply(f"***Ops... qualcosa è andato storto!***", ephemeral=True)

    if role.id in [r.id for r in inter.author.roles]:
      await inter.author.remove_roles(role)
      return await inter.reply(f"🙃 Ti ho rimosso il colore `{inter.component.label}`!", ephemeral=True)
    
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
    await inter.reply(f"👉 Ti ho aggiunto il colore `{inter.component.label}`!", ephemeral=True)
    
  #-------------------------------------------------------#
    
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    
    nitro_role = discord.utils.get(after.guild.roles, name="Nitro Booster")
    if nitro_role not in before.roles or nitro_role in after.roles:
      return
    
    channelID = await self.config.guild(after.guild).channelID()
    messageID = await self.config.guild(after.guild).messageID()
    
    channel = self.bot.get_channel(channelID)
    
    if channel is None:
      return
    
    msg = await channel.fetch_message(messageID)
    
    if msg is None:
      return

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
