import asyncio
import datetime
from asyncio import sleep

import discord
from discord.ext import commands, tasks

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop.start()
        self.message.start()
    
    @tasks.loop(hours = 1)
    async def message(self):
        channel = self.bot.get_channel(733067878030508173)
        evento_natalizio = self.bot.get_channel(776579327315279931)
        embed = discord.Embed(colour = discord.Colour.dark_green(), title = channel.guild.name, description = f"**Grandi novità! <a:rainbow_hype:740844953231556612> Corri a scoprirle sulla nuova categoria Role-Play! <:wumpus_gift:777473503058198558>**")
        def is_bot(message):
            return message.author.id == self.bot.user.id
        await channel.purge(limit = 40, check = is_bot)
        await channel.send(embed = embed)
            
def setup(bot):
  bot.add_cog(Events(bot))
