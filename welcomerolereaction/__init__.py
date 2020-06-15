from .welcomerolereaction import WelcomeRoleReaction

async def setup(bot):
  welcomerolereaction = WelcomeRoleReaction(bot)
  
  bot.add_cog(welcomerolereaction)
