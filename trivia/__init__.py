from redbot.core.bot import Red
from .trivia import trivia

def setup(bot : Red):
    quiz = trivia(bot)
    bot.add_cog(quiz)
    quiz.checker()
