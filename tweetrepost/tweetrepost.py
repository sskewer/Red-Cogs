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
    tweets = api.search_tweets(f"from:{str(tweet_user)}", count = 5, tweet_mode = "extended")
    # Getting Tweet Data
    try:
      input_data = tweets[0]._json
    except IndexError:
      return
    # Getting Image
    try:
      image_url = input_data["entities"]["media"][0]["media_url"]
    except IndexError:
      image_url = None
    # Webhook Post
    try:
      requests.post(
        "https://Fortnite.mettiushyper.repl.co/webhook",
        headers = {
          "webhook_url": api_tokens["webhook_url"],
        },
        json = {
          "text": input_data["full_text"],
          "image": image_url,
          "timestamp": input_data["created_at"],
          "color": "#ffffff",
          "translate_language": "it",
        },
      )
    except:
      return
    

def setup(bot):
  bot.add_cog(TweetRepost(bot))
