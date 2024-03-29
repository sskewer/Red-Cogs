import deepl
import tweepy
import logging
import datetime
import dateutil.parser

import discord
from discord.ext import tasks
from redbot.core import commands, Config
from discord_webhook import DiscordWebhook, DiscordEmbed

logging.basicConfig(format = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s', datefmt = '%y-%m-%d %H:%M:%S')
log = logging.getLogger("red.tweetrepost")

BaseCog = getattr(commands, "Cog", object)


# REMEMBER TO SET PARAMETERS BELOW USING THIS COMMAND
# [p]set api TweetRepost tweet_user,XXXXX webhook_url,XXXXX consumer_key,XXXXX consumer_secret,XXXXX access_token,XXXXX access_token_secret,XXXXX


class TweetRepost(BaseCog):
  
  def __init__(self, bot):
    super().__init__()
    self.bot = bot
    
    self.config = Config.get_conf(self, identifier=4000121212000335, force_registration=True)
    default_global = {"last_id": 0}
    self.config.register_global(**default_global)
    
    self.look_for_new_tweets.start()
    
    
  def cog_unload(self):
    self.look_for_new_tweets.cancel()
    
  
  # Look for new tweets code
  @tasks.loop(minutes = 10)
  async def look_for_new_tweets(self):
    
    await self.bot.wait_until_ready()
    
    log.info("Looking for new tweets to post...")
    try:
      api_tokens = await self.bot.get_shared_api_tokens('TweetRepost')
    except:
      return
    auth = tweepy.OAuth1UserHandler(
      api_tokens["consumer_key"], 
      api_tokens["consumer_secret"], 
      api_tokens["access_token"], 
      api_tokens["access_token_secret"]
    )
    api = tweepy.API(auth)
    tweets = api.user_timeline(screen_name = api_tokens['tweet_user'], count = 4, trim_user = True, exclude_replies = True, include_rts = False, tweet_mode = "extended")
    to_post = []
    for tweet in tweets:
      # Getting tweet data
      input_data = tweet._json
      # Getting image
      try:
        if "media" in input_data["entities"]:
          image = input_data["entities"]["media"][0]["media_url"]
        else:
          image = None
      except:
        image = None
      # Extracting important data
      to_post.append({
        "id": int(tweet.id),
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
      log.info(f"Found {str(len(to_post))} new tweet(s). Getting ready to send if needed...")
    # Webhook Posts
    for post in to_post:
      try:
        translated_text = deepl.translate(source_language = "EN", target_language = "IT", text = post["text"])
        webhook = DiscordWebhook(url = api_tokens["webhook_url"], rate_limit_retry = True)
        embed = DiscordEmbed(description = translated_text, color='00ABEE')
        embed.set_image(url = post["image"])
        embed.set_timestamp(post["timestamp"])
        embed.set_footer(text = "Twitter", icon_url = "https://media.discordapp.net/attachments/763039440200400917/1000338562631356486/20160903181541Twitter_bird_logo.png")
        webhook.add_embed(embed)
        webhook.execute()
        await self.config.last_id.set(post["id"])
      except:
        pass
    log.info("Waiting for 10 minutes...")

    
  @look_for_new_tweets.error
  async def look_for_new_tweets_error(self, error):
    log.error("Error in the task. Restarting the loop...", exc_info = True)
    return self.look_for_new_tweets.restart()

      
def setup(bot):
  bot.add_cog(TweetRepost(bot))
