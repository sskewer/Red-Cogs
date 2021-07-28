  
from .votesystem import VoteSystem

def setup(bot):
    bot.add_cog(VoteSystem(bot))
