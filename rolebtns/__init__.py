from dislash import SlashClient

from .rolebtns import RoleBtns


def setup(bot):
    cog = RoleBtns(bot)

    bot.add_cog(cog)

    if not hasattr(bot, "slash"):
        bot.slash = SlashClient(bot)
