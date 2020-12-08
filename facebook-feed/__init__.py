from .facebook-feed import FacebookFeed

def setup(bot):
    bot.add_cog(FacebookFeed(bot))
