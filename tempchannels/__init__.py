from dislash import SlashClient

from .tempchannels import TempChannels


def setup(bot):
    cog = TempChannels(bot)

    bot.add_cog(cog)

    if not hasattr(bot, "slash"):
        bot.slash = SlashClient(bot)
