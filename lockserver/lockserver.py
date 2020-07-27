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
    @commands.has_permissions(ban_members=True)
    async def lockserver(self, ctx):
        member = ctx.guild.get_member(ctx.message.author.id)
        everyonePermissions = ctx.guild.default_role.permissions
        perms_on = discord.Permissions(send_messages=True)
        perms_off = discord.Permissions(send_messages=False)
        
        if everyonePermissions.send_messages == True:
            await ctx.guild.default_role.edit(permissions=perms_off, reason=f"{member.display_name} ha bloccato il server")
            embed=discord.Embed(description=f"Il server è ora bloccato per l'invio di messaggi.", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
            embed.set_author(name="|  Blocco Server", url=member.avatar_url)
            embed.set_footer(text=f"Richiesto da {member.display_name}")
            await ctx.send(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.guild.default_role.edit(permissions=perms_on, reason=f"{member.display_name} ha sbloccato il server")
            embed2=discord.Embed(description=f"Il server è ora sbloccato per l'invio di messaggi.", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
            embed2.set_author(name="|  Blocco Server", url=member.avatar_url)
            embed2.set_footer(text=f"Richiesto da {member.display_name}")
            await ctx.send(embed=embed2)
            await ctx.message.delete()
    
