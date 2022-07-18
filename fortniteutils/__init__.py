from dislash import SlashClient

from .fortniteutils import FortniteUtils


def setup(bot):
    cog = FortniteUtils(bot)

    bot.add_cog(cog)

    if not hasattr(bot, "slash"):
        bot.slash = SlashClient(bot)
