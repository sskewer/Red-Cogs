from .faq import FaqCommand

def setup(bot):
    bot.add_cog(FaqCommand(bot))
