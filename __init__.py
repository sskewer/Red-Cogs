from .welcomerolereaction import WelcomeRoleReaction

def setup(bot):
    bot.add_cog(WelcomeRoleReaction(bot))