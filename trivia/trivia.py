import time
import asyncio
import datetime
import discord
import random

from discord.ext import tasks
from redbot.core import Config, commands
from redbot.core.bot import Red
from pymongo import MongoClient

reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
arrow_reactions = ["⏮", "◀", "▶", "⏭", "🛑"]

client = MongoClient("mongodb+srv://Kitbash:6j68WjZGI3Nmvw8Q@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = client.FortniteITA
coll = db["level-system"]
setup_coll = db["level-config"]

def role_check(ctx, roles):
    for n, role in enumerate(roles):
        role = ctx.guild.get_role(role)
        roles[n] = role
    return len(set(ctx.author.roles).intersection(set(roles))) > 0

async def post(self, force = False):
    guild = self.bot.get_guild(454261607799717888)
    setup = await self.config.guild(guild).setup()
    reaction_check = await self.config.guild(guild).reaction()
    if force != True:
        if setup["enabled"] == False:
            return
    if reaction_check != {}:
        return
    hex_int = int(setup['color'].replace("#", "0x"), 16)
    questions = await self.config.guild(guild).questions()
    if len(questions) < 1:
        # Nessuna domanda memorizzata, va inviato un avviso
        return await guild.get_channel(680459534463926294).send(":warning: **Attenzione:** Le domande memorizzate nel DB sono finite, usate il comando **`?domanda`** per aggiungerne altre.")
    question = random.choice(questions)
    questions.remove(question)
    await self.config.guild(guild).questions.set(questions)
    time = datetime.datetime.now() + datetime.timedelta(hours = int(question['time'][0])-1, minutes = int(question['time'][1]))
    time = datetime.datetime(time.year, time.month, time.day, time.hour)
    all_answers = question['incorrect_answers']
    all_answers.append(question['correct_answer'])
    random.shuffle(all_answers)
    correct_answer = all_answers.index(question['correct_answer'])
    value = ""
    for n, answer in enumerate(all_answers):
        value += f"**{n + 1}.** {answer}\n"
    embed = discord.Embed(title = question['question'], description = value.strip(), color = hex_int, timestamp = time)
    embed.set_footer(text = "Quiz in svolgimento", icon_url = guild.icon_url)
    try:
        embed.set_image(url = question['image'])
    except:
        pass
    msg = await guild.get_channel(setup['channel']).send(embed = embed)
    for n, answer in enumerate(all_answers):
        await msg.add_reaction(reactions[n])
    data = {
        "message" : msg.id,
        "correct" : correct_answer,
        "users" : [],
        "time" : datetime.datetime.timestamp(time + datetime.timedelta(hours = 1))
    }
    await self.config.guild(guild).reaction.set(data)

async def create_embed(self, question):
    guild = self.bot.get_guild(454261607799717888)
    time = question['time']
    for n, el in enumerate(time):
        el = str(el)
        if len(el) == 1:
            el = "0" + el
        time[n] = el
    user_incorrect = ""
    for incorrect in question["incorrect_answers"]:
        user_incorrect += f"• {incorrect}\n"
    setup = await self.config.guild(guild).setup()
    hex_int = int(setup["color"].replace("#", "0x"), 16)
    embed = discord.Embed(title = question['question'], color = hex_int)
    embed.add_field(name = "Risposta Corretta", value = f"• {question['correct_answer']}", inline = False)
    embed.add_field(name = "Risposte Errate", value = user_incorrect, inline = False)
    try:
        embed.set_image(url = question["image"])
    except:
        pass
    embed.set_footer(icon_url = guild.icon_url, text = f"Durata del quiz impostata a {time[0]}:{time[1]}")
    return embed

def update_db(userID, guildID, point):
    userLevel = coll.find_one({ "guild": str(guildID), "user": str(userID) })
    if userLevel == None:
        userLevel = {
            "points": 0,
            "level": 0,
            "timestamp": round((datetime.datetime.now().timestamp() - 60) * 1000)
        };
    levelUser = userLevel["level"]
    toNextLevel = 8 * ((levelUser + 1) ** 2) + 85 * levelUser + 110 + levelUser*100;
    toPreviousLevel = 8 * (levelUser ** 2) + 85 * (levelUser - 1) + 110 + (levelUser - 1)*100;
    while (userLevel["points"] + point) >= toNextLevel:
        levelUser += 1
        toNextLevel = 8 * ((levelUser + 1) ** 2) + 85 * levelUser + 110 + levelUser*100;
    coll.update_many({ "guild": str(guildID), "user": str(userID) }, { "$set": {
        "points": userLevel["points"] + point,
        "level": levelUser,
        "timestamp": round((datetime.datetime.now().timestamp() - 60) * 1000)
    } }, upsert = True)

async def close_post(self):
    guild = self.bot.get_guild(454261607799717888)
    setup = await self.config.guild(guild).setup()
    reaction = await self.config.guild(guild).reaction()
    if reaction == {}:
        return
    msg = await guild.get_channel(setup['channel']).fetch_message(int(reaction['message']))
    splitted_answers = msg.embeds[0].description.split("\n")
    correct_answer = int(reaction['correct'])
    correct = splitted_answers[correct_answer]
    index = correct.index('.') + 4
    time = datetime.datetime.now() - datetime.timedelta(hours = 1)
    time = datetime.datetime(time.year, time.month, time.day, time.hour)
    embed = discord.Embed(title = msg.embeds[0].title, description = f"```{str(correct[index:])}```", color = msg.embeds[0].color, timestamp = time)
    embed.set_footer(icon_url = guild.icon_url, text = "Quiz terminato")
    try:
        embed.set_thumbnail(url = msg.embeds[0].image.url)
    except:
        pass
    await msg.clear_reactions()
    await msg.edit(embed = embed)
    await self.config.guild(guild).reaction.set({})

async def reaction_confirm(self, ctx, msg):
    await msg.add_reaction("✅")
    await msg.add_reaction("❎")
    def reaction_check(reaction, user):
        return user.id == ctx.message.author.id and ["✅", "❎"].count(str(reaction.emoji)) > 0 and reaction.message.id == msg.id
    try:
        reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check, timeout=60.0)
        if str(reaction.emoji) == "✅":
            return True
        else:
            return False
    except asyncio.TimeoutError:
        return False


BaseCog = getattr(commands, "Cog", object)

class trivia(BaseCog):
    """Pubblicare domande quotidianamente"""
    # Cog creato da MettiusHyper#2100 e Simo#2417

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=4000121111111131, force_registration=True)
        default_guild = {"questions": [], "setup" : {"color" : "#1a80e4", "time" : 12, "channel" : 680459534463926294, "enabled" : True}, "reaction" : {}}
        self.config.register_guild(**default_guild)
        self.post_checker.start()
        self.close_checker.start()
        
    def cog_unload(self):
        self.post_checker.cancel()
        self.close_checker.cancel()

    #--------------# COMMANDS #--------------#

    @commands.group(name="trivia")
    @commands.guild_only()
    async def trivia(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            pass

    @trivia.command()
    async def force(self, ctx: commands.Context):
        """Posta forzatamente il quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833, 454268394464870401]):
            reaction_check = await self.config.guild(ctx.guild).reaction()
            if reaction_check != {}:
                return await ctx.message.add_reaction("🚫")
            await post(self, True)
            await ctx.message.add_reaction("✅")

    @trivia.command()
    async def close(self, ctx: commands.Context):
        """Chiude forzatamente il quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833, 454268394464870401]):
            reaction = await self.config.guild(ctx.guild).reaction()
            if reaction == {}:
                return await ctx.message.add_reaction("🚫")
            await close_post(self)
            await ctx.message.add_reaction("✅")
    
    @trivia.command()
    async def cleardb(self, ctx: commands.Context):
        """Resettare le domande"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            msg = await ctx.send("Sicuro di **resettare** le domande?")
            check = await reaction_confirm(self, ctx, msg)
            if check == True:
                await self.config.guild(ctx.guild).questions.set([])
                await self.config.guild(ctx.guild).reaction.set({})
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
            await msg.delete()
    
    @trivia.command()
    async def enable(self, ctx: commands.Context):
        """Attivare il post automatico dei quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            setup = await self.config.guild(ctx.guild).setup()
            if setup["enabled"] == False:
                setup.update({ "enabled" : True })
                await self.config.guild(ctx.guild).setup.set(setup)
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
                    
    @trivia.command()
    async def disable(self, ctx: commands.Context):
        """Disattivare il post automatico dei quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            setup = await self.config.guild(ctx.guild).setup()
            if setup["enabled"] == True:
                setup.update({ "enabled" : False })
                await self.config.guild(ctx.guild).setup.set(setup)
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
    
    #---------------# SETUP #---------------#
    
    @trivia.command()
    async def current(self, ctx: commands.Context):
        """Visualizzare la impostazioni correnti"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            setup = await self.config.guild(ctx.guild).setup()
            color = setup["color"]
            hex_int = int(color.replace("#", "0x"), 16)
            embed = discord.Embed(colour = hex_int, title = "Impostazioni Trivia", timestamp = datetime.datetime.utcnow())
            embed.add_field(name = "Color", value = f"`{color}`", inline = True)
            embed.add_field(name = "Time", value = f"{setup['time']}:00", inline = True)
            embed.add_field(name = "Channel", value = f"<#{setup['channel']}>", inline = True)
            embed.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
            await ctx.send(embed = embed)

    @trivia.command()
    async def color(self, ctx: commands.Context, value):
        """Modificare il colore dell'embed del quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            if value.startswith("#"):
                setup = await self.config.guild(ctx.guild).setup()
                setup.update({"color" : value})
                await self.config.guild(ctx.guild).setup.set(setup)
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
            
    @trivia.command()
    async def time(self, ctx: commands.Context, value : int):
        """Modificare l'ora di invio del quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            if value < 23 and value >= 0:
                setup = await self.config.guild(ctx.guild).setup()
                setup.update({"time" : value})
                await self.config.guild(ctx.guild).setup.set(setup)
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
    
    @trivia.command()
    async def channel(self, ctx: commands.Context, value : discord.TextChannel):
        """Modificare il canale di invio del quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            setup = await self.config.guild(ctx.guild).setup()
            setup.update({"channel" : value.id})
            await self.config.guild(ctx.guild).setup.set(setup)
            await ctx.message.add_reaction("✅")

    #--------------# STAFF COMMANDS #--------------#

    @commands.guild_only()
    @commands.command()
    async def domanda(self, ctx : commands.Context):
        if role_check(ctx, [659513332218331155, 454268394464870401, 454262524955852800, 720221658501087312, 659513332218331155]):
            #check for limit
            questions = await self.config.guild(ctx.guild).questions()
            if len(questions) > 15:
                return await ctx.send("Il **limite massimo** per le domande è stato raggiunto!\nProva ad eliminarne qualcuna con il comando `?trivia remove`")
            new_question = {}
            
            def r_check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            data = [
                ["question", "Qual è la **domanda**?"],
                ["correct_answer", "Qual è la **risposta corretta**?"],
                ["incorrect_answers", "Scrivi ora le **risposte errate**, separate da una `,`."],
                ["image", "Invia ora l'immagine come **allegato**, altrimenti rispondi `No`."],
                ["time", "Quale sarà la **durata** del quiz? Usa il formato `HH:MM`."]
            ]

            for el in data:
                temp = await ctx.send(el[1])
                try:
                    raw = await self.bot.wait_for('message', check=r_check, timeout=300.0)
                except:
                    return
                #custom checks
                if el[0] == "question":
                    if len(raw.content) > 256:
                        return await ctx.send("La **lughezza massima** per la domanda (256 caratteri) è stata superata, riprovare!")
                
                elif el[0] == "image":
                    if raw.attachments == []:
                        stored_image = None
                    else:
                        format_check = raw.attachments[0].filename.lower()
                        if format_check.endswith((".png", ".jpg", ".jpeg", ".gif", ".tiff", ".bmp")) == True:
                            image_file = await raw.attachments[0].to_file();
                            stored_image = await ctx.guild.get_channel(816212393922658306).send(content = f"**File Image Storing**\n{new_question['question']}", file = image_file)
                        else:
                            return await ctx.send("L'immagine allegata non è un **formato valido**, riprovare!")
                elif el[0] == "time":
                    time = raw.content.split(":")
                    try:
                        for n, element in enumerate(time):
                            time[n] = int(time[n])
                    except:
                        return await ctx.send("Specifica un'orario nel **formato corretto** (`HH:MM`), riprovare!")
                elif el[0] == "incorrect_answers":
                    incorrect_answers = raw.content.split(",")
                    for n, answer in enumerate(incorrect_answers):
                        incorrect_answers[n] = answer.strip()
                
                #new_question insertion, with custom stuff
                if el[0] == "image":
                    if stored_image != None:
                        new_question.update({ el[0]: stored_image.attachments[0].url })
                elif el[0] == "time":
                    new_question.update({el[0] : time})
                elif el[0] == "incorrect_answers":
                    new_question.update({el[0] : incorrect_answers})
                else:
                    new_question.update({ el[0] : raw.content })
                
                await temp.delete()
                await raw.delete()

            embed = await create_embed(self, new_question)

            msg = await ctx.send(content = "Reagisci con ✅ per **aggiungere la domanda**.", embed = embed)
            check = await reaction_confirm(self, ctx, msg)
            if check == True:
                questions = await self.config.guild(ctx.guild).questions()
                questions.append(new_question)
                await self.config.guild(ctx.guild).questions.set(questions)
                await msg.edit(content = "Domanda **aggiunta** con successo!")
            else:
                await ctx.message.add_reaction("🚫")
            await msg.clear_reactions()

    @trivia.command(aliases = ["db"])
    async def list(self, ctx: commands.Context, value: int = None):
        """Visualizzare la lista delle domande"""
        if role_check(ctx, [659513332218331155, 454268394464870401, 454262524955852800, 720221658501087312, 659513332218331155]):
            questions = await self.config.guild(ctx.guild).questions()
            setup = await self.config.guild(ctx.guild).setup()
            hex_int = int(setup["color"].replace("#", "0x"), 16)
            if len(questions) < 1:
                return await ctx.send(content = "Non riesco a trovare **domande memorizzate** nel database.\nPuoi utilizzare il comando **`?domanda`** per aggiungerne altre.")         
            if value is None:
                embed = discord.Embed(title = "Lista Domande", description = "```?trivia lista <numero>```", color = hex_int)
                embed.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
                for n, el in enumerate(questions):
                    embed.add_field(name = f"Domanda {n + 1}", value = el['question'], inline = False)
                await ctx.send(embed = embed)
            else:
                try:
                    question = questions[value - 1]
                    embed = await create_embed(self, question)
                    await ctx.send(content = f"Domanda **{value}** di {str(len(questions))}", embed = embed)
                except:
                    await ctx.message.add_reaction("🚫")

    @trivia.command()
    async def remove(self, ctx: commands.Context, value: int):
        """Rimuovere un quiz dal database"""
        if role_check(ctx, [454262524955852800, 454262403819896833, 454268394464870401]):
            questions = await self.config.guild(ctx.guild).questions()
            try:
                question = questions[value - 1]
            except:
                return await ctx.message.add_reaction("🚫")
            embed = await create_embed(self, question)
            msg = await ctx.send(content = f"Sicuro di **rimuovere** il seguente quiz?", embed = embed)
            check = await reaction_confirm(self, ctx, msg)
            if check == True:
                questions.remove(question)
                await self.config.guild(ctx.guild).questions.set(questions)
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("🚫")
            await msg.delete()

    @trivia.command()
    async def edit(self, ctx: commands.Context, value: int):
        """Modificare un quiz del database"""
        if role_check(ctx, [454262524955852800, 454262403819896833, 454268394464870401]):
            questions = await self.config.guild(ctx.guild).questions()
            try:
                question = questions[value - 1]
            except:
                return await ctx.message.add_reaction("🚫")
            embed = await create_embed(self, question)
            msg = await ctx.send(content = f"Sicuro di **modificare** il seguente quiz?", embed = embed)
            check = await reaction_confirm(self, ctx, msg)
            if check == False:
                try:
                    await msg.delete()
                except:
                    pass
                await ctx.message.add_reaction("🚫")
            else:
                def r_check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                await msg.delete()
                new_question = {
                    "question" : question["question"],
                    "correct_answer" : question["correct_answer"],
                    "incorrect_answers" : question["incorrect_answers"],
                    "time": question["time"]
                }
                try:
                    new_question.update({ "image": question["image"] })
                except:
                    pass
                
                data = [
                    ["question", "Scrivi ora la **domanda aggiornata**, altrimenti rispondi `Skip`."],
                    ["correct_answer", "Scrivi ora la **risposta corretta aggiornata**, altrimenti rispondi `Skip`."],
                    ["incorrect_answers", "Scrivi ora le **risposte errate aggiornate**, separate da una `,` o altrimenti rispondi `Skip`."],
                    ["image", "Invia ora l'**immagine aggiornata**, altrimenti rispondi `No` per rimuovere o `Skip`."],
                    ["time", "Scrivi ora la **nuova durata** del quiz usando il formato `HH:MM`, altrimenti rispondi `Skip`."]
                ]

                for el in data:
                    temp = await ctx.send(el[1])
                    try:
                        raw = await self.bot.wait_for('message', check=r_check, timeout=300.0)
                    except:
                        return
                    if raw.content.lower() != "skip":
                        if el[0] == "question":
                            if len(raw.content) > 256:
                                return await ctx.send("La **lughezza massima** per la domanda (256 caratteri) è stata superata, riprovare!")
                        elif el[0] == "image":
                            if raw.content.lower() == "no":
                                try:
                                    del new_question[el[0]]
                                except:
                                    pass
                                stored_image = None
                            if raw.attachments == []:
                                stored_image = None
                            else:
                                format_check = raw.attachments[0].filename.lower()
                                if format_check.endswith((".png", ".jpg", ".jpeg", ".gif", ".tiff", ".bmp")) == True:
                                    image_file = await raw.attachments[0].to_file();
                                    stored_image = await ctx.guild.get_channel(816212393922658306).send(content = f"**File Image Storing**\n{new_question['question']}", file = image_file)
                                else:
                                    return await ctx.send("L'immagine allegata non è un **formato valido**, riprovare!")
                        elif el[0] == "time":
                            time = raw.content.split(":")
                            try:
                                for n, element in enumerate(time):
                                    time[n] = int(time[n])
                            except:
                                return await ctx.send("Specifica un'orario nel **formato corretto** (`HH:MM`), riprovare!")
                        elif el[0] == "incorrect_answers":
                            incorrect_answers = raw.content.split(",")
                            for n, answer in enumerate(incorrect_answers):
                                incorrect_answers[n] = answer.strip()
                        
                        if el[0] == "image":
                            if stored_image != None:
                                new_question.update({ el[0]: stored_image.attachments[0].url })
                        elif el[0] == "time":
                            new_question.update({el[0] : time})
                        elif el[0] == "incorrect_answers":
                            new_question.update({el[0] : incorrect_answers})
                        else:
                            new_question.update({ el[0] : raw.content })
                    
                    await temp.delete()
                    await raw.delete()

                if new_question == question:
                    return await ctx.send("Non hai effettuato **nessuna modifica** alla domanda!")

                embed = await create_embed(self, new_question)

                msg = await ctx.send(content = "Reagisci con ✅ per **modificare la domanda**.", embed = embed)
                check = await reaction_confirm(self, ctx, msg)
                if check == True:
                    questions.remove(question)
                    questions.append(new_question)
                    await self.config.guild(ctx.guild).questions.set(questions)
                    await msg.edit(content = "Domanda **modificata** con successo!")
                else:
                    await msg.edit(content = "Modifica della domanda **annullata** con successo!", embed = None)
                    await ctx.message.add_reaction("🚫")
                await msg.clear_reactions()

    #---------------# EVENTS #---------------#

    @tasks.loop(minutes=1, reconnect=True)
    async def post_checker(self):
        # Check if post a question
        guild = self.bot.get_guild(454261607799717888)
        setup = await self.config.guild(guild).setup()
        time = int(setup["time"])
        now = datetime.datetime.now()
        if now.hour == time:
            await post(self)
                                                                                                        
    @post_checker.before_loop
    async def before_post_checker(self):
        await self.bot.wait_until_ready()
                            
    @tasks.loop(minutes=10, reconnect=True)
    async def close_checker(self):
        # Check if questions ended
        guild = self.bot.get_guild(454261607799717888)
        setup = await self.config.guild(guild).setup()
        reaction = await self.config.guild(guild).reaction()
        checking = await guild.get_channel(816212393922658306).send(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Controllando eventuali quiz terminati...")
        if reaction == {}:
            return await checking.channel.send(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Nessun quiz terminato trovato")    
        if datetime.datetime.fromtimestamp(reaction['time']) < datetime.datetime.now():
            await close_post(self)
            await checking.channel.send(content = f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Quiz terminato in <#{str(setup['channel'])}>\n<https://discord.com/channels/454261607799717888/{str(setup['channel'])}/{str(reaction['message'])}>")
        else:
            await checking.channel.send(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Nessun quiz terminato trovato")
    
    @close_checker.before_loop
    async def close_post_checker(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
        guild = self.bot.get_guild(454261607799717888)
        data = await self.config.guild(guild).reaction()
        member = guild.get_member(payload.user_id)
        if member.bot == False:
            if data != {} and data != None:
                if data["message"] == payload.message_id:
                    if payload.user_id not in data["users"]:
                        if str(payload.emoji) in reactions:
                            setup = setup_coll.find_one({"guild" : "454261607799717888"})
                            users = [ int(i) for i in setup["users"] ]
                            roles = [ guild.get_role(int(i)) for i in setup["roles"]]
                            if member.roles not in roles and member.id not in users:  
                                if reactions.index(str(payload.emoji)) == data["correct"]:
                                    update_db(payload.user_id, guild.id, 100)
                                    await guild.get_channel(816212393922658306).send(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Risposta corretta per <@!{payload.user_id}>\n<https://discord.com/channels/454261607799717888/{str(payload.channel_id)}/{str(payload.message_id)}>")
                            users = data["users"]
                            users.append(payload.user_id)
                            data.update({"users" : users})
                            await self.config.guild(guild).reaction.set(data)
                    msg = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(payload.emoji, guild.get_member(payload.user_id))
