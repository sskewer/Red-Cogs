from .randomnick import RandomNick

def setup(bot):
    bot.add_cog(RandomNick(bot))
