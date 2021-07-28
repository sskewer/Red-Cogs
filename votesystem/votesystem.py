import discord
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class VoteSystem(BaseCog):
  
  def __init__(self, bot):
    self.bot = bot
      
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
    guild = self.bot.get_guild(454261607799717888)
    member = guild.get_member(payload.user_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if member.bot == False and payload.channel_id == 807985160703180850 and message.author.id == self.bot.user.id and str(payload.emoji) == "✅":
      embed = discord.Embed(description = f"[`Richiesta presa in carico da {member}`]({message.jump_url})", color = discord.Colour.from_rgb(19, 123, 196))
      await message.edit(content = "", embed = embed)
      await message.clear_reactions()
      await message.unpin(reason = f"Richiesta presa in carico da {member}")

def setup(bot):
  bot.add_cog(VoteSystem(bot))
