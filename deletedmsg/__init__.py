
from dislash import SlashClient

from .deletedmsg import DeletedMsg


def setup(bot):
    cog = DeletedMsg(bot)

    bot.add_cog(cog)

    if not hasattr(bot, "slash"):
        bot.slash = SlashClient(bot)
