from .trivia import trivia

async def setup(bot):
    bot.add_cog(trivia(bot))
