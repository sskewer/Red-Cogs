import tweepy
import requests

import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

# REMEMBER TO SET PARAMETERS BELOW USING THIS COMMAND
# [p]set api TweetRepost
#   webhook_url,XXXXXXXXXXXXXXXXXXXXXXXXX
#   api_key,XXXXXXXXXXXXXXXXXXXXXXXXX
#   api_key_secret,XXXXXXXXXXXXXXXXXXXXXXXXX
#   access_token,XXXXXXXXXXXXXXXXXXXXXXXXX
#   access_token_secret,XXXXXXXXXXXXXXXXXXXXXXXXX

tweet_user = "FortniteStatus" # Remember to change this parameter according to your needs

class TweetRepost(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    try:
      webhook_url = (await self.bot.get_shared_api_tokens('TweetRepost'))['webhook_url']
      api_key = (await self.bot.get_shared_api_tokens('TweetRepost'))['api_key']
      api_key_secret = (await self.bot.get_shared_api_tokens('TweetRepost'))['api_key_secret']
      access_token = (await self.bot.get_shared_api_tokens('TweetRepost'))['access_token']
      access_token_secret = (await self.bot.get_shared_api_tokens('TweetRepost'))['access_token_secret']
    except:
      return
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    try:
      tweets = api.user_timeline(screen_name=tweet_user, count=5, tweet_mode='extended', exclude_replies=True, include_rts=False)
    except:
      return
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
