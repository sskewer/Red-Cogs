from redbot.core.bot import Red

from .trivia import trivia

async def setup(bot: Red):
    quiz = trivia(bot)
    await quiz.initialize()
    bot.add_cog(quiz)
