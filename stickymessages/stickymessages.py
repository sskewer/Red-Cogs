import discord
from contextlib import suppress
from redbot.core import commands

#---------# Reminder Embed #---------#

embeds = {
  674689662509514752: discord.Embed(
    title = "Errore di traduzione da segnalare?",
    description = "In questo canale, puoi segnalare solo errori di traduzione in lingua :flag_it: italiana.\nNel farlo, si prega di **taggare <@!623929121482735637>** e allegare uno screenshot in cui sia ben visibile l'errore che si vuole segnalare. Tutti i post che non sono rilevanti saranno rimossi.",
    color = discord.Colour.from_rgb(19, 123, 196)
  ),
  454261608324268063: discord.Embed(
    description = "**Unisciti al nostro canale [>> Crea Canali <<](https://discord.gg/mdxtrbr) per creare in automatico un tuo canale completamente personalizzabile. Il canale si autodistruggerà quando si svuoterà, ma potrai crearne uno nuovo. Buon game!**  <a:kitbash_sound:717042518939795527>",
    color = 0xf1c40f
  ),
}

#------------------------------------#

BaseCog = getattr(commands, "Cog", object)

class StickyMessages(BaseCog):
  """Lasciare un reminder come ultimo messaggio del canale"""
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    to_send = embeds[message.channel.id]
    if to_send != None and message.author.id != 710078958036582471:
      async for msg in message.channel.history(limit=10):
        if msg.author.id == 710078958036582471 and len(msg.embeds) > 0:
          if msg.embeds[0].description == to_send.description:
            await msg.delete()
      await message.channel.send(embed=to_send)
      
  @commands.guild_only()
  @commands.command()
  async def reset(self, ctx):
    """Avviare il reminder associato al canale"""
    epicstaff = ctx.guild.get_role(454262403819896833)
    moderatori = ctx.guild.get_role(454262524955852800)
    guardiani = ctx.guild.get_role(454268394464870401)
    if epicstaff in ctx.author.roles or moderatori in ctx.author.roles or guardiani in ctx.author.roles:
      try:
        await ctx.channel.send(embed=embeds[ctx.channel.id])
        await ctx.message.delete()
      except:
        await ctx.message.add_reaction("🚫")
    else:
      await ctx.message.delete()
