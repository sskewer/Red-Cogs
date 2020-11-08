import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class FaqCommand(BaseCog):
  """Ottenere un collegamento diretto alla FAQ indicata"""
  
  def __init__(self, bot):
    self.bot = bot
        
    @commands.guild_only()
    @commands.command(name='faqtest')
    async def faq_test(self, ctx, *, args: str = None):
      if ctx.message.mentions == []:
        member = None
      else:
        for mention in ctx.message.mentions:
          args = args.replace(f"<@!{mention.id}>", "")
        channel = ctx.guild.get_channel(774706975400919090)
        messages = await channel.history(limit=50).flatten()
        titles = []
        for message in messages:
          complete_message = message.content.splitlines( )
          for line in complete_message:
            if "**[" in line:
              title = line[line.index("**")+2:line.rindex("**")]
              titles.append(title)
        
      # Search Function
      for n, title in enumerate(titles):
        if args in title:
          found_message = messages[n]
          found_title = title
        
      # Embed Message
      embed = discord.Embed(description=f"[`{found_title}`]({found_message.jump_url})", color=discord.Colour.from_rgb(19, 123, 196))
      if ctx.message.mentions == []:
        await ctx.send(embed=embed)
      else:
        epicstaff = ctx.guild.get_role(454262403819896833)
        moderatori = ctx.guild.get_role(454262524955852800)
        guardiano = ctx.guild.get_role(454268394464870401)
        vindertech = ctx.guild.get_role(659513332218331155)
        if epicstaff in ctx.author.roles or moderatori in ctx.author.roles or guardiano in ctx.author.roles or vindertech in ctx.author.roles:
          content = "";
          for mention in ctx.message.mentions:
            content = content + "<@!" + mention.id + "> "
          await ctx.send(content=content, embed=embed)
        else:
          await ctx.send(embed=embed)
            
      # Remove Author Message
      await ctx.message.delete()
