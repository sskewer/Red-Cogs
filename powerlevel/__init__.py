from dislash import SlashClient

from .powerlevel import PowerLevel


def setup(bot):
    cog = PowerLevel(bot)

    bot.add_cog(cog)

    if not hasattr(bot, "slash"):
        bot.slash = SlashClient(bot)
