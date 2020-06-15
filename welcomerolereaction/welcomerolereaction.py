import asyncio

from contextlib import suppress
import discord
from redbot.core import commands

from discord import Embed, Guild, Member, Role
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context, Greedy, group
from discord.utils import get

import requests
from discord import Webhook, RequestsWebhookAdapter


#----------------# CONFIG #----------------#

guild_id = 454261607799717888
role_id = 721988422041862195
reaction_name = '<:fnit_gift:601709109955395585>'
message_id = 721990614228664361
webhook_id = 721997644955779102
welcome_channel_id = 603955376286728226
welcome_messages = ['{user}, benvenuto nel team No Sweat!', '{user}? Il team No Sweat ti stava aspettando!', 'Team No Sweat, finalmente anche {user} è qui con noi!']

#------------------------------------------#


BaseCog = getattr(commands, "Cog", object)

class WelcomeRoleReaction(BaseCog):
    """Role reaction and give the welcome by webhook to a specific channel"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()        
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Vars
        role = get(user.guild.roles, id=role_id)
        welcome_channel = get(user.guild.channels, id=welcome_channel_id)
        user: discord.User = self.bot.get_user(int(payload.user_id))
        guild: discord.Guild = self.bot.config.get(guild_id)
        
        # Reaction Role
        if payload.guild_id is None:
            return
        if user.bot:
            return
        member: discord.Member = await guild.fetch_member(payload.user_id)
        if member is None:
            return
        if role in member.roles:
            return
        if payload.emoji.name == reaction_name:
            await member.add_roles(role)
        
        # Embed
        random_message = random.choice(welcome_messages)
        embed = discord.Embed(description="{user}, benvenuto!".replace("{user}", member.mention), color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=member.display_name, icon_url=user.avatar_url)
        embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        
        # Welcome Webhook
        hooks = await welcome_channel.webhooks()
        hook = get(hooks, id=webhook_id)
        await hook.send(embed=embed)
        
