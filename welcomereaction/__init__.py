from .welcomereaction import WelcomeReaction

async def setup(bot):
    bot.add_cog(WelcomeReaction(bot))
