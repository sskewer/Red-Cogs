from .lockserver import LockServer

def setup(bot):
    bot.add_cog(LockServer(bot))
