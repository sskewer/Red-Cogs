from .trivia import trivia

def setup(bot):
    bot.add_cog(trivia(bot))
