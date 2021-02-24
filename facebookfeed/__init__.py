from redbot.core.bot import Red

from .facebookfeed import FacebookFeed

def setup(bot: Red):
    bot.add_cog(FacebookFeed(bot))
