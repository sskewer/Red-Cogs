from .stickymessages import StickyMessages

def setup(bot):
    bot.add_cog(StickyMessages(bot))
