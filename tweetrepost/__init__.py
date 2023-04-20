from .tweetrepost import TweetRepost

def setup(bot):
    bot.add_cog(TweetRepost(bot))
