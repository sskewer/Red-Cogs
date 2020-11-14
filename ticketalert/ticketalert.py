import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class TicketAlert(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_message(self, message):
    if message.channel.id == 683363814137266207:
      channel = message.guild.get_channel(663742727225212928)
      vindertech_role = message.guild.get_role(659513332218331155)
      referente_vindertech_role = message.guild.get_role(720221658501087312)
      embed = discord.Embed(description = f"[`Nuova richiesta di supporto per voi`]({message.jump_url})", color = discord.Colour.from_rgb(19, 123, 196))
      embed.set_footer(text = "Reagisci per prendere in carico la segnalazione")
      sent_message = await channel.send(content = f"{referente_vindertech_role.mention} {vindertech_role.mention}", embed = embed)
      await sent_message.add_reaction("✅")
      def check(reaction, user):
        return reaction.message.id == sent_message.id and user.id != self.bot.user.id and str(reaction.emoji) == "✅"
      reaction, member = await self.bot.wait_for('reaction_add', check=check)
      await channel.send("Triggered")
      embed = discord.Embed(description = f"[`Richiesta presa in carico da {member}`]({message.jump_url})", color = discord.Colour.from_rgb(19, 123, 196))
      await sent_message.edit(content = "", embed = embed)
      sent_message = await channel.fetch_message(sent_message.id)
      await sent_message.clear_reactions()

def setup(bot):
  bot.add_cog(TicketAlert(bot))
