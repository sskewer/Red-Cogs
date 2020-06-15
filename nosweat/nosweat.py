import asyncio
import datetime
import secrets
from contextlib import suppress

import discord
from discord.ext import tasks
from discord import Embed, Guild, Member, Role
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context, Greedy, group
from discord.utils import get

from redbot.core import checks, Config, commands
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

import requests
from discord import Webhook, RequestsWebhookAdapter

#----------------# CONFIG #----------------#

role_id = 721988422041862195
reaction_id = 601709109955395585
message_id = 721990614228664361
webhook_id = 721997644955779102
welcome_channel_id = 603955376286728226
webhook_token = "Cv83ufD1LJdcGNtRfWmBUOHaIxYpB6aMOx5H_8MdL82mlfnUK8PRsVvZa3NvuKRreyLi"
welcome_messages = ['{user}, benvenuto nel team No Sweat!', '{user}? Il team No Sweat ti stava aspettando!', 'Team No Sweat, finalmente anche {user} è qui con noi!', 'Guardate chi è arrivato? Anche {user} nel Team No Sweat!]

#------------------------------------------#

class NoSweat(commands.Cog):
  """Role reaction and give the welcome by webhook to a specific channel"""
  def __init__(self, bot):
    self.bot = bot
    
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    # Vars
    guild = self.bot.get_guild(payload.guild_id)
    if not guild:
      return
    role = get(guild.roles, id=role_id)
    welcome_channel = get(guild.channels, id=welcome_channel_id)
    member = guild.get_member(payload.user_id)

    # Reaction Role
    if member is None:
        return
    if role in member.roles:
        return
    if payload.emoji.id == reaction_id and payload.message_id == message_id:
        await member.add_roles(role)
        # Embed
        random_message = secrets.choice(welcome_messages)
        replaced_message = random_message.replace("{user}", member.mention)
        embed = discord.Embed(description=replaced_message, color=0x0066cc, timestamp=datetime.datetime.utcnow())
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        # Welcome Webhook
        webhook = Webhook.partial(webhook_id, webhook_token,\
                                  adapter=RequestsWebhookAdapter())
        await webhook.send(embed=embed)
