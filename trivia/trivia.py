import datetime
from asyncio import sleep
import discord
import requests
import random
from requests.api import post
from redbot.core import Config, commands
from redbot.core.bot import Red
import asyncio
import nest_asyncio
nest_asyncio.apply()
__import__('IPython').embed()

reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

async def post(self, guild):
    setup = await self.config.guild(guild).setup()
    hex_int = int(setup['color'].replace("#", "0x"), 16)
    questions = await self.config.guild(guild).questions()
    if len(questions) < 1:
        #nessuna domanda memorizzata, va inviato un avviso
        return await guild.get_channel(680459534463926294).send(":warning: Le domande memorizzate nel database sono finite, usate il comando `?domanda` per aggiungerne altre :warning:")
    question = random.choice(questions)
    embed = discord.Embed(description = f"**{question['question']}**", color = hex_int)
    embed.set_footer(text = guild.name, icon_url = guild.icon_url)
    try:
        embed.set_image(url = question['image'])
    except:
        pass
    all_answers = question['incorrect_answers']
    all_answers.append(question['correct_answer'])
    await guild.get_channel(454268474534133762).send(str(all_answers))
    random.shuffle(all_answers)
    correct_answer = all_answers.index(question['correct_answer'])
    value = ""
    for n, answer in enumerate(all_answers):
        value += f"**{n + 1}.** `{answer}`"
    embed.add_field(name = "Risposte:", value = value.strip())
    msg = await guild.get_channel(setup['channel']).send(embed = embed)
    for n, answer in enumerate(all_answers):
        await msg.add_reaction(reactions[n])
    data = {
        "message" : msg.id,
        "correct" : correct_answer,
        "users" : []
    }
    await self.config.guild(guild).reaction.set(data)

async def checker(self):
    await self.client.get_channel(454268474534133762).send("ciao")
    guild = self.bot.get_guild(454261607799717888)
    setup = await self.config.guild(guild).setup()
    time = setup["time"]
    now = datetime.datetime.now()
    if now.hour < time:
        post_time = datetime.datetime(now.year, now.month, now.day, time)
    else:
        hop = now + datetime.timedelta(day = 1) - datetime.timedelta(hours = now.hour - time)
        post_time = datetime.datetime(hop.year, hop.month, hop.day, hop.hour)
    delta_time = post_time - now
    await self.client.get_channel(454268474534133762).send(str(delta_time))
    await sleep(delta_time.seconds)
    while True:
        await post(self, guild)
        await sleep(86400) #1 day
    
def run_and_get(coro):
    task = asyncio.create_task(coro)
    asyncio.get_running_loop().run_until_complete(task)
    return task.result()

class trivia(commands.Cog):
    #Pubblicare domande quotidianamente
    #Cog creato da MettiusHyper#2100

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=4000121111111131, force_registration=True)
        default_global = {}
        default_guild = {"questions": [], "score" : {}, "setup" : {"color" : "#1a80e4", "time" : 12, "channel" : 680459534463926294}, "reaction" : {}}
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        run_and_get(checker(self))
        
    #--------------# COMMANDS #--------------#

    @commands.guild_only()
    @commands.command()
    async def domanda(self, ctx : commands.Context, *, question : str):
        allowed_roles = [536214242685091860, 454268394464870401, 454262524955852800, 454262403819896833]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            await ctx.send("Qual è la risposta corretta?")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            correct_answer = await self.bot.wait_for('message', check=check)

            await ctx.send("Scrivi ora le risposte errate, separate da una `,`")
            incorrect_answers_raw = await self.bot.wait_for('message', check=check)
            incorrect_answers = incorrect_answers_raw.content.split(",")
            for n, answer in enumerate(incorrect_answers):
                incorrect_answers[n] = answer.strip()
            question = {
                "question" : question,
                "correct_answer" : correct_answer.content,
                "incorrect_answers" : incorrect_answers
            }
            await ctx.send("Invia ora l'immagine, rispondi con `No` se vuoi che la domanda non contenga alcuna immagine.")
            image = await self.bot.wait_for('message', check=check)
            if image.content != "No":
                if image.attachments != []:
                    question.update({"image" : image.attachments[0].url})
                else:
                    question.update({"image" : image.content})

            user_incorrect = ""
            for incorrect in question["incorrect_answers"]:
                user_incorrect += f"{incorrect}\n"
            setup = await self.config.guild(ctx.guild).setup()
            hex_int = int(setup["color"].replace("#", "0x"), 16)
            embed = discord.Embed(
                description = f"**{question['question']}**", color = hex_int
            )
            embed.add_field(name = "Risposta Corretta", value = question["correct_answer"])
            embed.add_field(name = "Risposte Errate", value = user_incorrect)
            try:
                embed.set_image(url = question["image"])
            except:
                pass
            msg = await ctx.send(content = "Reagisci con <:FNIT_ThumbsUp:454640434380013599> per aggiungere la domanda", embed = embed)
            await msg.add_reaction("<:FNIT_ThumbsUp:454640434380013599>")
            await msg.add_reaction("<:FNIT_ThumbsDown:454640434610700289>")
            
            def reaction_check(reaction, user):
                return user == ctx.message.author and (str(reaction.emoji) == "<:FNIT_ThumbsUp:454640434380013599>" or str(reaction.emoji) == "<:FNIT_ThumbsDown:454640434610700289>")
            reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if str(reaction.emoji) == "<:FNIT_ThumbsUp:454640434380013599>":
                questions = await self.config.guild(ctx.guild).questions()
                questions.append(question)
                await self.config.guild(ctx.guild).questions.set(questions)
                await ctx.send("Domanda aggiunta!")
            await msg.clear_reactions()
            
    @commands.group(name="trivia")
    @commands.guild_only()
    async def trivia(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            pass
        
    @trivia.command()
    async def force_post(self, ctx: commands.Context):
        """Posta forzatamente il quiz"""
        allowed_roles = [454262524955852800, 454262403819896833]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            await post(self, ctx.guild)
    
    @trivia.command(aliases = ["lb"])
    async def leaderboard(self, ctx: commands.Context):
        allowed_roles = [454262524955852800, 454262403819896833]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            score = await self.config.guild(ctx.guild).score()
            setup = await self.config.guild(ctx.guild).setup()
            hex_int = int(setup["color"].replace("#", "0x"), 16)
            description = ""
            for n, el in enumerate(score):
                description += f"**{n + 1}.** {ctx.guild.get_member(el)}(`{el}`)\n"
            await ctx.send(embed = discord.Embed(
                title = "LeaderBoard",description = description.strip(), color = hex_int
            ).set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url))

    @trivia.command()
    async def current(self, ctx: commands.Context):
        allowed_roles = [454262524955852800, 454262403819896833]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            setup = await self.config.guild(ctx.guild).setup()
            color = setup["color"]
            hex_int = int(color.replace("#", "0x"), 16)
            embed = discord.Embed(colour = hex_int, title = "Impostazioni Trivia", timestamp = datetime.datetime.utcnow())
            embed.add_field(name = "Color", value = f"`{color}`", inline = True)
            embed.add_field(name = "Time", value = f"{setup['time']}:00", inline = True)
            embed.add_field(name = "Channel", value = f"<#{setup['channel']}>", inline = True)
            embed.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
            await ctx.channel.send(embed = embed)
    
    @trivia.command()
    async def color(self, ctx: commands.Context, value):
        """Modificare il colore dell'embed nel database"""
        allowed_roles = [454262524955852800, 454262403819896833]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            if value.startswith("#"):
                setup = await self.config.guild(ctx.guild).setup()
                setup.update({"color" : value})
                await self.config.guild(ctx.guild).setup.set(setup)
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
            
    @trivia.command()
    async def time(self, ctx: commands.Context, value : int):
        """Modificare l'ora nel quale il sondaggio avrà luogo"""
        allowed_roles = [454262524955852800, 454262403819896833]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            if value < 23 and value >= 0:
                setup = await self.config.guild(ctx.guild).setup()
                setup.update({"time" : value})
                await self.config.guild(ctx.guild).setup.set(setup)
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
    
    @trivia.command()
    async def channel(self, ctx: commands.Context, value : discord.TextChannel):
        """Modificare il canale in cui viene inviato il quiz"""
        allowed_roles = [454262524955852800, 454262403819896833]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            setup = await self.config.guild(ctx.guild).setup()
            setup.update({"channel" : value.id})
            await self.config.guild(ctx.guild).setup.set(setup)
            await ctx.message.add_reaction("✅")

  #------------# EVENT #------------#
                    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
        guild = self.bot.get_guild(454261607799717888)
        data = await self.config.guild(guild).reaction()
        if guild.get_member(payload.user_id).bot == False:
                if data["message"] == payload.message_id:
                    if payload.user_id not in data["users"]:
                        if str(payload.emoji) in reactions:
                            await guild.get_channel(454268474534133762).send("ab")
                            if reactions.index(str(payload.emoji)) == data["correct"]:
                                score = await self.config.guild(guild).score()
                                try:
                                    old_score = score[str(payload.user_id)]
                                except:
                                    old_score = 0
                                score.update({payload.user_id : old_score + 1})
                                await self.config.guild(guild).score.set(score)
                            users = data["users"]
                            users.append(payload.user_id)
                            data.update({"users" : users})
                            await self.config.guild(guild).reaction.set(data)
                    msg = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(payload.emoji, guild.get_member(payload.user_id))
