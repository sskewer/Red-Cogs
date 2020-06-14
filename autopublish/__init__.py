from .autopublish import AutoPublish

def setup(bot):
    bot.add_cog(AutoPublish(bot))
