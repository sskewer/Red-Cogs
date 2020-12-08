from .facebookfeed import FacebookFeed

def setup(bot):
    feed = FacebookFeed(bot)
    bot.add_cog(feed)
    bot.loop.create_task(daily.checker())
