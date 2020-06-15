from .welcomerolereaction import WelcomeRoleReaction

async def setup(bot):
    bot.add_cog(WelcomeRoleReaction(bot))
