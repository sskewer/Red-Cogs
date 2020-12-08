import asyncio
from redbot.core.bot import Red

from .facebookfeed import FacebookFeed

def setup(bot: Red):
    feed = FacebookFeed(bot)
    bot.add_cog(feed)
    asyncio.create_task(feed.checker())
