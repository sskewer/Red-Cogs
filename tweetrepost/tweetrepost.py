import tweepy
import requests

import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

# REMEMBER TO SET PARAMETERS BELOW USING THIS COMMAND
# [p]set api TweetRepost
#   webhook_url,XXXXXXXXXXXXXXXXXXXXXXXXX
#   bearer_token,XXXXXXXXXXXXXXXXXXXXXXXXX

tweet_user_id = "FortniteStatus" # Remember to change this parameter according to your needs

class TweetRepost(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    try:
      webhook_url = (await self.bot.get_shared_api_tokens('TweetRepost'))['webhook_url']
      bearer_token = (await self.bot.get_shared_api_tokens('TweetRepost'))['bearer_token']
    except:
      return
    client = tweepy.Client(bearer_token = bearer_token)
    response = client.get_users_tweets(tweet_user_id, max_results = 5)
    for tweet in response.data:
      print(tweet.id)
      print(tweet.text)
    try:
      requests.post(
        "https://Fortnite.mettiushyper.repl.co/webhook",
        headers = {
          "webhook_url": webhook_url,
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
