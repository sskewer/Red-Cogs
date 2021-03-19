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
      channel = message.guild.get_channel(807985160703180850)
      vindertech_role = message.guild.get_role(659513332218331155)
      referente_vindertech_role = message.guild.get_role(720221658501087312)
      embed = discord.Embed(description = f"[`Nuova richiesta di supporto per voi`]({message.jump_url})", color = discord.Colour.from_rgb(19, 123, 196))
      embed.set_footer(text = "Reagisci per prendere in carico la segnalazione")
      sent_message = await channel.send(content = f"{referente_vindertech_role.mention} {vindertech_role.mention}", embed = embed)
      await sent_message.add_reaction("✅")
      await sent_message.pin(reason = "Nuova richiesa di supporto")
      def system_pin_check(msg):
        return msg.is_system()
      await channel.purge(limit=10, check=system_pin_check)
      
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
      guild = self.bot.get_guild(454261607799717888)
      member = guild.get_user(payload.user_id)
      channel = guild.get_channel(payload.channel_id)
      message = await channel.fetch_message(payload.message_id)
      if member.bot == False and payload.channel_id == 807985160703180850 and message.author.id == self.bot.user.id and str(payload.emoji) == "✅":
        print("Sono scemo!")
        embed = discord.Embed(description = f"[`Richiesta presa in carico da {member}`]({message.jump_url})", color = discord.Colour.from_rgb(19, 123, 196))
        await message.edit(content = "", embed = embed)
        await message.clear_reactions()
        await message.unpin(reason = f"Richiesta presa in carico da {member}")

def setup(bot):
  bot.add_cog(TicketAlert(bot))
