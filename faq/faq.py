import discord
from contextlib import suppress
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class Faq(BaseCog):
  """Ottenere un collegamento diretto alla FAQ indicata"""
  
  def __init__(self, bot):
    self.bot = bot
        
  @commands.guild_only()
  @commands.command()
  async def faq(self, ctx):
    args = ctx.message.content.replace("?faq ", "")
    if args != None:
      if ctx.message.mentions == []:
        member = None
      else:
        for mention in ctx.message.mentions:
          args = args.replace(f"<@!{mention.id}>", "")
      if args.isspace() == False:
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
        found_message = None
        for n, title in enumerate(titles):
          args = args.replace(" ", "")
          search_title = title.replace(" ", "")
          if args.lower() in search_title.lower():
            found_message = messages[n]
            found_title = title
        
        # Embed Message
        if found_message != None:
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
                content = content + "<@!" + str(mention.id) + "> "
              await ctx.send(content=content, embed=embed)
            else:
              await ctx.send(embed=embed)
            
          # Remove Author Message
          await ctx.message.delete()
        else:
          await ctx.message.delete()
      else:
        await ctx.message.delete()
    else:
      await ctx.message.delete()
        
