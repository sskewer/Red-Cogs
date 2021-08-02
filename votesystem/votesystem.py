import discord
from uuid import uuid4
from redbot.core import Config, commands
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
      
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
    # Token Generation
    token = uuid4()
    # Variables
    guild = self.bot.get_guild(payload.guild_id)
    channel_id = await self.config.guild(guild).channel()
    message_id = await self.config.guild(guild).message()
    if channel_id is None or message_id is None:
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
      link = self.vote_config["url"] + str(token)
      embed = discord.Embed(title = "Votazione Pubblica - Concorso \"Investigatore Cosmico\"", description = f"La richiesta per registrare la tua preferenza al fine di selezionare le Candidature vincitrici è stata elaborata. Il sistema di voto è anonimo e limitato ad una sola votazione per utente, in quanto il link è univoco per ognuno che decide di votare.", color = discord.Color.gold())
      embed.add_field(name="*Ricordati che, dopo l'invio del modulo, non sarà possibile votare nuovamente.*", value=f"[***Cliccando qui puoi accedere alla votazione. Grazie della collaborazione!***]({link})")
      await payload.member.send(embed=embed)

def setup(bot):
  bot.add_cog(VoteSystem(bot))
