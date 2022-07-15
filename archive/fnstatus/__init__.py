from .fnstatus import FnStatus

def setup(bot):
    bot.add_cog(FnStatus(bot))
