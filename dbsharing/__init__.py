from .dbsharing import DatabaseSharing

def setup(bot):
    bot.add_cog(DatabaseSharing(bot))
