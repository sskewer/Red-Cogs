import json
import discord
import os

from aiohttp import web
from redbot.core import Config, commands
from discord.ext import tasks
from redbot.core.bot import Red


#---------------# Get Epic Account #---------------#

async def get_epic_account(self, guild, user):
    epiclinking = self.bot.get_cog("EpicLinking")
    verified_user_id = await epiclinking.settings.guild(guild).verified_user_id()
    if str(user) in verified_user_id:
        epic_account = { "id": verified_user_id[str(user)] }
        if len(epiclinking.clients) > 0:
            try:
                epic_user = await epiclinking.clients[0].fetch_user(epic_user["id"])
                epic_account["name"] = epic_user.display_name if epic_user != None else None
            except:
                pass
        return epic_account
    else:
        return {}


#------------------# Cog Code #------------------#

BaseCog = getattr(commands, "Cog", object)

app = web.Application()
routes = web.RouteTableDef()

class DatabaseSharing(BaseCog):
    """Cog created for local database sharing"""
    
    def __init__(self, bot):
        self.bot = bot
        self.webserver_port = os.environ.get('PORT', 5050)
        self.web_server.start()
        
        @routes.get('/epiclinking/{guild}/{user}')
        async def epic_linking(request):
            user = request.match_info['user']
            guild_id = request.match_info['guild']
            guild = self.bot.get_guild(int(guild_id))
            if guild is None:
                return web.Response(text = json.dumps({ "status": 404, "error": "Invalid or non-existent guild ID" }))
            if user is None:
                return web.Response(text = json.dumps({ "status": 504, "error": "Invalid or non-existent user ID" })) 
            result = await get_epic_account(self, guild, int(user))
            if result == {}:
                return web.Response(text = json.dumps({ "status": 400, "error": "No data found for the specified user" })) 
            result["status"] = 200
            return web.Response(text = json.dumps(result))
        
        app.add_routes(routes)
    
    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host = '0.0.0.0', port = self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()
