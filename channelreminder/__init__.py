from .channelreminder import ChannelReminder

def setup(bot):
    bot.add_cog(ChannelReminder(bot))
