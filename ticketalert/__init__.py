from .ticketalert import TicketAlert

def setup(bot):
    bot.add_cog(TicketAlert(bot))
