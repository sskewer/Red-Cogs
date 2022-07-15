from dislash import SlashClient

from .nitroboosters import NitroBoosters


def setup(bot):
    cog = NitroBoosters(bot)

    bot.add_cog(cog)

    if not hasattr(bot, "slash"):
        bot.slash = SlashClient(bot)
