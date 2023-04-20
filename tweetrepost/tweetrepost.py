import tweepy
import requests

import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

# REMEMBER TO SET PARAMETERS BELOW USING THIS COMMAND
# [p]set api TweetRepost webhook_url,XXXXX consumer_key,XXXXX consumer_secret,XXXXX access_token,XXXXX access_token_secret,XXXXX

tweet_user = "FortniteStatus" # Remember to change this parameter according to your needs

class TweetRepost(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    try:
      api_tokens = await bot.get_shared_api_tokens('TweetRepost')
    except:
      return
    auth = tweepy.OAuth1UserHandler(
      api_tokens["consumer_key"], 
      api_tokens["consumer_secret"], 
      api_tokens["access_token"], 
      api_tokens["access_token_secret"]
    )
    api = tweepy.API(auth)
    try:
      tweets = api.search_tweets(str(tweet_user), count = 5, tweet_mode = "extended")
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
