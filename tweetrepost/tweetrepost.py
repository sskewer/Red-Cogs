import requests
import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class TweetRepost(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    try:
      requests.post(
        "https://Fortnite.mettiushyper.repl.co/webhook",
        headers = {
          "webhook_url" : WEBHOOK_URL
        },
        json = {
          "text": input_data["text"],
          "image": input_data["image"],
          "timestamp": input_data["timestamp"],
          "color": "#ffffff",
          "translate_language": "it",
        },
      )
    except:
      pass
    

def setup(bot):
  bot.add_cog(TweetRepost(bot))
