import tweepy
import asyncio
import requests
import dateutil.parser

import discord
from contextlib import suppress
from redbot.core import commands, Config

BaseCog = getattr(commands, "Cog", object)


# REMEMBER TO SET PARAMETERS BELOW USING THIS COMMAND
# [p]set api TweetRepost tweet_user,XXXXX webhook_url,XXXXX consumer_key,XXXXX consumer_secret,XXXXX access_token,XXXXX access_token_secret,XXXXX


class TweetRepost(BaseCog):
  
  def __init__(self, bot):
    super().__init__(*args, **kwargs)
    self.bot = bot
    self.config = Config.get_conf(self, identifier=4000121212000335, force_registration=True)
    default_global = {"last_id": 0}
    self.config.register_global(**default_global)
    self.bot.loop.create_task(self.look_for_new_tweets())
        
  async def look_for_new_tweets(self):
    while True:

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
      tweets = api.search_tweets(f"from:{str(api_tokens["tweet_user"])}", count = 10, tweet_mode = "extended")
      to_post = []
      for tweet in tweets:
        # Getting tweet data
        input_data = tweet._json
        # Getting image
        try:
          image = input_data["entities"]["media"][0]["media_url"]
        except IndexError:
          image = None
        # Extracting important data
        to_post.append({
          "id": tweet.id,
          "text": input_data["full_text"],
          "image": image,
          "timestamp": dateutil.parser.parse(input_data["created_at"]).timestamp(),
        })
      # Last posted tweet check
      last_id = await self.config.last_id()
      to_post.sort(key = lambda x: x['timestamp'])                               
      try:
        index = [t["id"] for t in to_post].index(last_id)
      except ValueError:
        index = -1
      if index != -1:
        to_post = to_post[index+1:]
      # Webhook Posts
      for post in to_post:
        try:
          requests.post(
            "https://Fortnite.mettiushyper.repl.co/webhook",
            headers = {
              "webhook_url": api_tokens["webhook_url"],
            },
            json = {
              "text": post["text"],
              "image": post["image"],
              "timestamp": post["timestamp"],
              "color": "#ffffff",
              "translate_language": "it",
            },
          )
          await self.config.last_id.set(to_post["id"])
        except:
          pass
        
      await asyncio.sleep(900)  # pause for 15 minutes


def setup(bot):
  bot.add_cog(TweetRepost(bot))
