import asyncio
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

BaseCog = getattr(commands, "Cog", object)

class NoSweat(Cog):
