from redbot.core.bot import Red

from .channelreminder import ChannelReminder

def setup(bot: Red):
    reminder = ChannelReminder(bot)
    bot.add_cog(reminder)
    bot.loop.create_task(reminder.checker())
