from redbot.core.bot import Red
from .trivia import trivia

def setup(bot : Red):
    trivia = trivia(bot)
    bot.add_cog(trivia)
    bot.loop.create_task(trivia.checker())
