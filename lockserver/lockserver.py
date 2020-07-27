import asyncio
import datetime

from contextlib import suppress
import discord
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class LockServer(BaseCog):
    """Lock the server and block everyone to send messages"""
    def __init__(self, bot):
        self.bot = bot
        
    @commands.guild_only()
    @commands.command(aliases=["serverlock"])
    @checks.has_permissions(ban_members=True)
    async def lockserver(self, ctx):
        member = ctx.guild.get_member(ctx.message.author.id)
        everyonePermissions = ctx.guild.default_role.permissions
        
        if everyonePermissions.send_messages === true:
            await ctx.guild.default_role.edit(permissions=send_messages, reason=f"{member.display_name} ha bloccato il server")
            embed=discord.Embed(description=f"La slowmode per questo canale è ora **{time}**", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
            embed.set_author(name="|  Blocco Server", url=member.avatar_url)
            embed.set_footer(text=f"Richiesta da {member.display_name}")
        else:
    
