import asyncio
import discord
import datetime
from uuid import uuid4
from redbot.core import checks, Config, commands
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Kitbash:6j68WjZGI3Nmvw8Q@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = client.FortniteITA

async def reaction_confirm(self, ctx, msg):
  await msg.add_reaction("✅")
  await msg.add_reaction("❎")
  def reaction_check(reaction, user):
    return user.id == ctx.message.author.id and ["✅", "❎"].count(str(reaction.emoji)) > 0 and reaction.message.id == msg.id
  try:
    reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check, timeout=60.0)
    if str(reaction.emoji) == "✅":
      return True
    else:
      return False
  except asyncio.TimeoutError:
    return False

BaseCog = getattr(commands, "Cog", object)

class VoteSystem(BaseCog):
  
  def __init__(self, bot):
    super().__init__()
    self.bot = bot    
    self.config = Config.get_conf(self, identifier=4000121111111111, force_registration = True)
    default_guild = { "enabled": True, "current": None, "name": None, "url": None, "channel": None, "message": None }
    self.config.register_guild(**default_guild)
    self.mongo = db["vote-system"]
  
  
  #---------------# SETUP #---------------#
  
  @commands.group(name="vote", aliases=["votesystem", "votation"])
  @commands.guild_only()
  async def _vs(self, ctx: commands.Context):
    """Vote System Cog by Simo#2471"""
    if ctx.invoked_subcommand is None:
        pass
      
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def current(self, ctx: commands.Context):
    """Visualizzare la impostazioni di voto correnti"""
    status = await self.config.guild(ctx.guild).enabled()
    if status == True:
      colour = discord.Color.green()
    else:
      colour = discord.Color.red()
    name = await self.config.guild(ctx.guild).name()
    if name is None:
      name = ctx.guild.name
    else:
      name = f"Concorso {name}"
    channel = await self.config.guild(ctx.guild).channel()
    message = await self.config.guild(ctx.guild).message()
    url = await self.config.guild(ctx.guild).url()
    embed = discord.Embed(colour = colour, title = "Impostazioni Sistema Voto", timestamp = datetime.datetime.utcnow())
    embed.add_field(name = "Canale", value = f"<#{channel}>", inline = True)
    embed.add_field(name = "Messaggio", value = f"[`{message}`](https://discord.com/channels/{ctx.guild.id}/{channel}/{message})", inline = True)
    embed.add_field(name = "Modulo Votazione", value = f"[*Cliccare qui per il modulo*]({url})", inline = False)
    embed.set_footer(text = name, icon_url = ctx.guild.icon_url)
    await ctx.send(embed = embed)
  
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def url(self, ctx: commands.Context, value: str):
    """Modificare l'url del modulo di voto nel database"""
    if value.startswith("https://docs.google.com/forms/"):
      current = max(value.split("/"), key=len)
      msg = await ctx.send("Impostando un nuovo modulo, **ripristinerai** il database per una nuova votazione.\nSei **sicuro** di procedere? Utilizza le reazioni per confermare o annullare l'operazione.")
      check = await reaction_confirm(self, ctx, msg)
      await msg.delete()
      if check == True:
        try:
          module = await self.config.guild(ctx.guild).current()
          self.mongo.delete_many({ "module": str(module) })
          await self.config.guild(ctx.guild).current.set(current)
          await self.config.guild(ctx.guild).url.set(value)
          await ctx.message.add_reaction("✅")
        except:
          await ctx.message.add_reaction("🚫")
      else:
        await ctx.message.add_reaction("🚫")
    else:
      await ctx.message.add_reaction("🚫")
      
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def name(self, ctx: commands.Context, *, value: str):
    """Modificare il nome della votazione nel database"""
    if len(value) > 0:
      name = f"\"{value}\""
    else:
      name = None
    await self.config.guild(ctx.guild).name.set(name)
    await ctx.message.add_reaction("✅")
      
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def channel(self, ctx: commands.Context, channel: discord.TextChannel):
    """Modificare l'ID del canale di voto nel database"""
    await self.config.guild(ctx.guild).channel.set(channel.id)
    await ctx.message.add_reaction("✅")
    
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def message(self, ctx: commands.Context, msg: int):
    """Modificare l'ID del messaggio di voto nel database"""
    channel_id = await self.config.guild(ctx.guild).channel()
    channel = ctx.guild.get_channel(channel_id)
    # Channel Check
    if channel_id is None or channel is None:
      return ctx.send("Per impostare il **messaggio di voto**, devi aver prima impostato il canale.\nUtilizza il comando **`[p]vote channel`** per configurare il canale di voto.")
    if len(str(msg)) != 18:
      return await ctx.message.add_reaction("🚫")
    try:
      message = await channel.fetch_message(msg)
      if message is not None:
        await self.config.guild(ctx.guild).message.set(msg)
        await ctx.message.add_reaction("✅")
        await message.add_reaction("✅")
      else:
        await ctx.message.add_reaction("🚫")
    except:
      await ctx.message.add_reaction("🚫")
      
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def enable(self, ctx: commands.Context):
    """Attivare la votazione con le impostazione correnti"""
    status = await self.config.guild(ctx.guild).enabled()
    if status == False:
      channel_id = await self.config.guild(ctx.guild).channel()
      message_id = await self.config.guild(ctx.guild).message()
      if channel_id is not None and message_id is not None:
        # Get Object
        channel = ctx.guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        # Remove Reactions
        await message.clear_reaction("🚫")
        await message.add_reaction("✅")
      await self.config.guild(ctx.guild).enabled.set(True)
      await ctx.message.add_reaction("✅")
    else:
      await ctx.message.add_reaction("🚫")
                    
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def disable(self, ctx: commands.Context):
    """Disattivare la votazione con le impostazione correnti"""
    status = await self.config.guild(ctx.guild).enabled()
    if status == True:
      channel_id = await self.config.guild(ctx.guild).channel()
      message_id = await self.config.guild(ctx.guild).message()
      if channel_id is not None and message_id is not None:
        # Get Object
        channel = ctx.guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        # Remove Reactions
        await message.clear_reaction("✅")
        await message.add_reaction("🚫")
      await self.config.guild(ctx.guild).enabled.set(False)
      await ctx.message.add_reaction("✅")
    else:
      await ctx.message.add_reaction("🚫")

  
  #------------# VOTE SYSTEM #------------#
  
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
    # Token Generation
    token = uuid4()
    # Variables
    guild = self.bot.get_guild(payload.guild_id)
    status = await self.config.guild(guild).enabled()
    name = await self.config.guild(guild).name()
    module = await self.config.guild(guild).current()
    url = await self.config.guild(guild).url()
    channel_id = await self.config.guild(guild).channel()
    message_id = await self.config.guild(guild).message()
    if url is None or channel_id is None or message_id is None:
      return
    # Get Object
    channel = guild.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    # Token Check
    token_list = self.mongo.find({})
    while len([x for x in list(token_list) if x["_id"] == token]) > 0:
      token = uuid4()
    # User Check
    user_check = self.mongo.find_one({ "user": str(payload.member.id) })
    # Name Check
    if name is None:
      name = ""
    # Script
    if status == True and payload.member.bot == False and payload.channel_id == channel.id and payload.message_id == message.id and str(payload.emoji) == "✅":
      if user_check is None:
        # Database Update
        self.mongo.insert_one({ "_id": str(token), "user": str(payload.member.id), "voted": False, "module": str(module) })
        # Send DM
        link = url + str(token)
        embed = discord.Embed(title = f"Votazione Pubblica - Concorso {name}", description = f"La richiesta per registrare la tua preferenza al fine di selezionare le Candidature vincitrici è stata elaborata. Il sistema di voto è anonimo e limitato ad una sola votazione per utente, in quanto il link è univoco per ognuno che decide di votare.", color = discord.Color.gold())
        embed.add_field(name="*Ricordati che, dopo l'invio del modulo, non sarà possibile votare nuovamente.*", value=f"[***Cliccando qui puoi accedere alla votazione. Grazie della collaborazione!***]({link})")
        await payload.member.send(embed=embed)
      # Reaction Remove
      msg = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
      await msg.remove_reaction(str(payload.emoji), guild.get_member(payload.user_id))

def setup(bot):
  bot.add_cog(VoteSystem(bot))
