import datetime
import discord

from redbot.core import Config, commands
from redbot.core.bot import Red


#---------------# Get Epic Account #---------------#

async def get_epic_account(self, guild, user):
    epiclinking = self.bot.get_cog("EpicLinking")
    verified_user_id = await epiclinking.settings.guild(guild).verified_user_id()
    if str(user.id) in verified_user_id:
        epic_account = { "id": verified_user_id[str(user.id)] }
        if len(epiclinking.clients) > 0:
            try:
                epic_user = await epiclinking.clients[0].fetch_user(epic_user["id"])
                epic_account["name"] = epic_user.display_name if epic_user != None else None
            except:
                pass
        return epic_account
    else:
        return {}


#------------------# Cog Code #------------------#

BaseCog = getattr(commands, "Cog", object)

class DatabaseSharing(BaseCog):
    """Cog created for local database sharing"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.guild_only()
    @commands.command()
    async def test(self, ctx, member: discord.Member):
        result = await get_epic_account(self, ctx.guild, member)
        await ctx.send(f"```json\n{str(result)}\n```")
        
