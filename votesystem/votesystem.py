import discord
import datetime
from uuid import uuid4
from redbot.core import checks, Config, commands
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Kitbash:6j68WjZGI3Nmvw8Q@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = client.FortniteITA

BaseCog = getattr(commands, "Cog", object)

class VoteSystem(BaseCog):
  
  def __init__(self, bot):
    super().__init__()
    self.bot = bot    
    self.config = Config.get_conf(self, identifier=4000121111111111, force_registration = True)
    default_guild = { "url": None, "channel": None, "message": None }
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
    channel = await self.config.guild(ctx.guild).channel()
    message = await self.config.guild(ctx.guild).message()
    url = await self.config.guild(ctx.guild).url()
    embed = discord.Embed(colour = discord.Color.gold(), title = "Impostazioni Sistema Voto", timestamp = datetime.datetime.utcnow())
    embed.add_field(name = "Canale", value = f"`<#{channel}>`", inline = True)
    embed.add_field(name = "Messaggio", value = f"[`{message}`](https://discord.com/channels/{ctx.guild}/{channel}/{message})", inline = True)
    embed.add_field(name = "Modulo Votazione", value = f"[*Cliccare qui per il modulo*]({url})", inline = False)
    embed.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
    await ctx.send(embed = embed)
  
  @_vs.command()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild = True)
  async def url(self, ctx: commands.Context, value: str):
    """Modificare l'url del modulo di voto nel database"""
    if value.startswith("https://docs.google.com/forms/"):
      await self.config.guild(ctx.guild).url.set(value)
      await ctx.message.add_reaction("✅")
    else:
      await ctx.message.add_reaction("🚫")
      
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
    if (await channel.fetch_message(msg)) is not None:
      await self.config.guild(ctx.guild).message.set(msg)
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
    # Script
    if user_check is None and payload.member.bot == False and payload.channel_id == channel.id and payload.message_id == message.id and str(payload.emoji) == "✅":
      # Database Update
      self.mongo.insert_one({ "_id": str(token), "user": str(payload.member.id), "voted": False })
      # Send DM
      link = url + str(token)
      embed = discord.Embed(title = "Votazione Pubblica - Concorso \"Investigatore Cosmico\"", description = f"La richiesta per registrare la tua preferenza al fine di selezionare le Candidature vincitrici è stata elaborata. Il sistema di voto è anonimo e limitato ad una sola votazione per utente, in quanto il link è univoco per ognuno che decide di votare.", color = discord.Color.gold())
      embed.add_field(name="*Ricordati che, dopo l'invio del modulo, non sarà possibile votare nuovamente.*", value=f"[***Cliccando qui puoi accedere alla votazione. Grazie della collaborazione!***]({link})")
      await payload.member.send(embed=embed)

def setup(bot):
  bot.add_cog(VoteSystem(bot))
