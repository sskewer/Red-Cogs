import discord
from uuid import uuid4
from redbot.core import commands
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Kitbash:6j68WjZGI3Nmvw8Q@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = client.FortniteITA

BaseCog = getattr(commands, "Cog", object)

class VoteSystem(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
    self.mongo = db["vote-system"]
    self.vote_config = {
      "url": "https://docs.google.com/forms/d/e/1FAIpQLSc_cZEdmgq23IR8_m6YjbVZTCeCqz2aS8zJ1nrLBWPL0vsmhQ/viewform?usp=pp_url&entry.1831324353=",
      "guild": 454261607799717888,
      "channel": 454268474534133762,
      "message": 869894908767502356
    }
      
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
    # Token Generation
    token = uuid4()
    # Variables
    guild = self.bot.get_guild(self.vote_config["guild"])
    channel = guild.get_channel(self.vote_config["channel"])
    message = await channel.fetch_message(self.vote_config["message"])
    # Token Check
    token_list = self.mongo.find({})
    while len([x for x in list(token_list) if x["_id"] == token]) > 0:
      token = uuid4()
    # User Check
    user_check = self.mongo.find({ "user": payload.member.id })
    print(list(user_check))
    # Script
    if len(list(user_check)) == 0 and payload.member.bot == False and payload.channel_id == channel.id and payload.message_id == message.id and str(payload.emoji) == "✅":
      # Database Update
      self.mongo.insert_one({ "_id": str(token), "user": str(payload.member.id) })
      # Send DM
      link = self.vote_config["url"] + str(token)
      embed = discord.Embed(title = "Votazione Pubblica - Concorso \"Investigatore Cosmico\"", description = f"La richiesta per registrare la tua preferenza al fine di selezionare le Candidature vincitrici è stata elaborata. Il sistema di voto è anonimo e limitato ad una sola votazione per utente, in quanto il link è univoco per ognuno che decide di votare.", color = discord.Color.gold())
      embed.add_field(name="*Ricordati che, dopo l'invio del modulo, non sarà possibile votare nuovamente.*", value=f"[***Cliccando qui puoi accedere alla votazione. Grazie della collaborazione!***]({link})")
      await payload.member.send(embed=embed)

def setup(bot):
  bot.add_cog(VoteSystem(bot))
