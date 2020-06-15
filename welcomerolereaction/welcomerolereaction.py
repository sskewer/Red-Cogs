import asyncio

from contextlib import suppress
import discord
from redbot.core import commands


#------------# CONFIG #------------#

role = 721988422041862195
reaction = '<:fnit_gift:601709109955395585>'
message = 721988332153733141
welcome_channel = 603955376286728226
welcome_message = ['{user}, benvenuto nel team No Sweat!', '{user}? Il team No Sweat ti stava aspettando!', 'Team No Sweat, finalmente anche {user} è qui con noi!']

#----------------------------------#


BaseCog = getattr(commands, "Cog", object)

class WelcomeRoleReaction(BaseCog):
    """Bind a role reaction to a message and give the welcome to a specific channel"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user)
