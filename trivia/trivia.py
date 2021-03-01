import asyncio
import datetime
import discord
import random

from asyncio import sleep
from discord.ext import tasks
from redbot.core import Config, commands
from redbot.core.bot import Red
from pymongo import MongoClient

reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
arrow_reactions = ["⏮", "◀", "▶", "⏭", "🛑"]

client = MongoClient("mongodb+srv://Kitbash:6j68WjZGI3Nmvw8Q@modmail.rsxw7.mongodb.net/FortniteITA?retryWrites=true&w=majority")
db = client.FortniteITA
coll = db["level-system"]

def update_db(userID, guildID, point):
    userLevel = coll.find_one({ "guild": str(guildID), "user": str(userID) })
    if userLevel == None:
      userLevel = {
        "points": 0,
        "level": 0,
        "timestamp": (datetime.datetime.now().timestamp() - 60) * 1000
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
      "timestamp": (datetime.datetime.now().timestamp() - 60) * 1000
    } }, upsert = True)

def role_check(ctx, roles):
    for n, role in enumerate(roles):
        role = ctx.guild.get_role(role)
        roles[n] = role
    return len(set(ctx.author.roles).intersection(set(roles))) > 0

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

async def lb_embed(self, description, pos):
    guild = self.bot.get_guild(454261607799717888)
    setup = await self.config.guild(guild).setup()
    hex_int = int(setup["color"].replace("#", "0x"), 16)
    if len(description) == 0:
        description = "Non trovo **nessun utente** da registrare in classifica!"
    else:
        description = description[pos]
    embed = discord.Embed(
        title = "Leaderboard", description = description.strip(), color = hex_int
    ).set_footer(text = guild.name, icon_url = guild.icon_url)
    return embed

def listify(description):
    a_description = []
    limit = 2048
    while len(description) > 0:
        if len(description) > limit:
            a_description.append(description[:limit])
            description = description[limit:]
        else:
            a_description.append(description)
            description = ""
    return a_description

async def post(self):
    guild = self.bot.get_guild(454261607799717888)
    setup = await self.config.guild(guild).setup()
    if setup["enabled"] == False:
        return
    hex_int = int(setup['color'].replace("#", "0x"), 16)
    questions = await self.config.guild(guild).questions()
    if len(questions) < 1:
        # Nessuna domanda memorizzata, va inviato un avviso
        return await guild.get_channel(680459534463926294).send(":warning: **Attenzione:** Le domande memorizzate nel DB sono finite, usate il comando **`?domanda`** per aggiungerne altre.")
    question = random.choice(questions)
    questions.remove(question)
    await self.config.guild(guild).questions.set(questions)
    time = datetime.datetime.now() + datetime.timedelta(hours = int(question['time'][0]), minutes = int(question['time'][0]))
    all_answers = question['incorrect_answers']
    all_answers.append(question['correct_answer'])
    random.shuffle(all_answers)
    correct_answer = all_answers.index(question['correct_answer'])
    value = ""
    for n, answer in enumerate(all_answers):
        value += f"**{n + 1}.** {answer}\n"
    embed = discord.Embed(title = question['question'], description = value.strip() ,color = hex_int, timestamp = time)
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
        "time" : datetime.datetime.timestamp(time)
    }
    await self.config.guild(guild).reaction.set(data)

async def close_post(self, post_message = None):
    guild = self.bot.get_guild(454261607799717888)
    setup = await self.config.guild(guild).setup()
    reaction = await self.config.guild(guild).reaction()
    if post_message == None:
        post_message = reaction['message']
    msg = await guild.get_channel(setup['channel']).fetch_message(int(post_message))
    await msg.clear_reactions()
    description = msg.embeds[0].description.split()
    correct_answer = description[reaction['correct']]
    correct_answer = correct_answer[7:]
    embed = discord.Embed(title = msg.embeds[0].title, description = correct_answer, color = msg.embeds[0].color, timestamp =  datetime.datetime.fromtimestamp(reaction['time']))
    embed.set_footer(icon_url = guild.icon_url, text = "Quiz terminato")
    await self.config.guild(guild).reaction.set({})

BaseCog = getattr(commands, "Cog", object)

class trivia(BaseCog):
    """Pubblicare domande quotidianamente"""
    # Cog creato da MettiusHyper#2100
                    
    #---------------# SETUP #---------------#
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=4000121111111131, force_registration=True)
        default_guild = {"questions": [], "score" : {}, "setup" : {"color" : "#1a80e4", "time" : 12, "channel" : 680459534463926294, "enabled" : True}, "reaction" : {}}
        self.config.register_guild(**default_guild)
        self.start_post.start()
        self.checker.start()
        
    def cog_unload(self):
        self.start_post.cancel()
        self.daily_post.cancel()
        self.checker.cancel()

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
            try:
                setup = await self.config.guild(ctx.guild).setup()
                temp = setup
                temp.update({ "enabled" : True })
                await self.config.guild(ctx.guild).setup.set(temp)
                await post(self)
                await self.config.guild(ctx.guild).setup.set(setup)
                await ctx.message.add_reaction("✅")
            except:
                await ctx.message.add_reaction("🚫")
    
    @trivia.command()
    async def close(self, ctx: commands.Context, msg_id: int = None):
        """Chiude forzatamente il quiz"""
        if role_check(ctx, [454262524955852800, 454262403819896833, 454268394464870401]):
            await close_post(self, msg_id)
            await ctx.message.add_reaction("✅")
    
    @trivia.command()
    async def clearlb(self, ctx: commands.Context):
        """Resettare la classifica"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            msg = await ctx.send("Sicuro di **resettare** la classifica?")
            await msg.add_reaction("✅")
            await msg.add_reaction("❎")
            def reaction_check(reaction, user):
                return user.id == ctx.message.author.id and ["✅", "❎"].count(str(reaction.emoji)) > 0 and reaction.message.id == msg.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check, timeout=60.0)        
                if str(reaction.emoji) == "✅":
                    await self.config.guild(ctx.guild).score.set({})
                    await msg.delete()
                    await ctx.message.add_reaction("✅")
                else:
                    await msg.delete()
                    await ctx.message.add_reaction("🚫")
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.message.add_reaction("🚫")
   
    @trivia.command()
    async def cleardb(self, ctx: commands.Context):
        """Resettare le domande"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            msg = await ctx.send("Sicuro di **resettare** le domande?")
            await msg.add_reaction("✅")
            await msg.add_reaction("❎")
            def reaction_check(reaction, user):
                return user.id == ctx.message.author.id and ["✅", "❎"].count(str(reaction.emoji)) > 0 and reaction.message.id == msg.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check, timeout=60.0)        
                if str(reaction.emoji) == "✅":
                    await self.config.guild(ctx.guild).questions.set([])
                    await self.config.guild(ctx.guild).reaction.set({})
                    await msg.delete()
                    await ctx.message.add_reaction("✅")
                else:
                    await msg.delete()
                    await ctx.message.add_reaction("🚫")
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.message.add_reaction("🚫")
    
    @trivia.command()
    async def test(self, ctx: commands.Context):
        """Testare gli errori di Mettius"""
        if role_check(ctx, [454262524955852800, 454262403819896833]):
            update_db(ctx.guild.id, ctx.author.id, 100)
            await ctx.message.add_reaction("✅")
    
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
            await msg.add_reaction("✅")
            await msg.add_reaction("❎")
            def reaction_check(reaction, user):
                return user.id == ctx.message.author.id and ["✅", "❎"].count(str(reaction.emoji)) > 0 and reaction.message.id == msg.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check, timeout=60.0)        
                if str(reaction.emoji) == "✅":
                    def check(m):
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
                    
                    await ctx.send(content = "Scrivi ora la **domanda aggiornata**, altrimenti rispondi `Skip`.")
                    try:
                        new_value = await self.bot.wait_for('message', check=check, timeout=300.0)
                    except:
                        return
                    if len(new_value.content) > 256:
                        return await ctx.send("La **lughezza massima** per la domanda (256 caratteri) è stata superata, riprovare!")
                    if new_value.content != "Skip":
                        new_question.update({ "question": new_value.content })
                    
                    await ctx.send("Scrivi ora la **risposta corretta aggiornata**, altrimenti rispondi `Skip`.")
                    try:
                        new_value = await self.bot.wait_for('message', check=check, timeout=300.0)
                    except:
                        return
                    if new_value.content != "Skip":
                        new_question.update({ "correct_answer": new_value.content })
                    
                    await ctx.send("Scrivi ora le **risposte errate aggiornate**, separate da una `,` o altrimenti rispondi `Skip`.")
                    try:
                        incorrect_answers_raw = await self.bot.wait_for('message', check=check, timeout=300.0)
                    except:
                        return
                    if incorrect_answers_raw.content != "Skip":
                        new_value = incorrect_answers_raw.content.split(",")
                        for n, answer in enumerate(new_value):
                            new_value[n] = answer.strip()
                        new_question.update({ "incorrect_answers": new_value })
                    
                    await ctx.send("Invia ora l'**immagine aggiornata**, altrimenti rispondi `No` per rimuovere o `Skip`.")
                    try:
                        image = await self.bot.wait_for('message', check=check, timeout=300.0)
                    except:
                        return
                    if image.content != "Skip":
                        if image.content == "No":
                            try:
                                del new_question["image"]
                            except:
                                pass
                        if image.attachments != [] and image.content != "No":
                            format_check = image.attachments[0].filename.lower()
                            if format_check.endswith((".png", ".jpg", ".jpeg", ".gif", ".tiff", ".bmp")) == True:
                                new_question.update({ "image": image.attachments[0].url })
                            else:
                                return await ctx.send("L'allegato non appartiene a un **formato immagine**, riprovare!")
                            
                    await ctx.send("Scrivi ora la **nuova durata** del quiz usando il formato `HH:MM`, altrimenti rispondi `Skip`.")
                    try:
                        time = await self.bot.wait_for('message', check=check, timeout=300.0)
                    except:
                        return
                    if time.content != "Skip":
                        time = time.content.split(":")
                        try:
                            for n, el in enumerate(time):
                                time[n] = int(time[n])
                        except:
                            return await ctx.send("Specifica una durata nel **formato corretto** (`HH:MM`), riprovare!")
                        new_question.update({ "time": time })
                            
                    if new_question == question:
                        return await ctx.send("Non hai effettuato **nessuna modifica** alla domanda!")
                    
                    confirm = await ctx.send(content = "Reagisci con <:FNIT_ThumbsUp:454640434380013599> per **modificare la domanda**.", embed = await create_embed(self, new_question))
                    await confirm.add_reaction("<:FNIT_ThumbsUp:454640434380013599>")
                    await confirm.add_reaction("<:FNIT_ThumbsDown:454640434610700289>")
                    def reaction_confirm(reaction, user):
                        return user == ctx.message.author and (str(reaction.emoji) == "<:FNIT_ThumbsUp:454640434380013599>" or str(reaction.emoji) == "<:FNIT_ThumbsDown:454640434610700289>") and reaction.message.id == confirm.id
                    reaction, user = await self.bot.wait_for('reaction_add', check=reaction_confirm, timeout=60.0)
                    if str(reaction.emoji) == "<:FNIT_ThumbsUp:454640434380013599>":
                        questions.remove(question)
                        questions.append(new_question)
                        await self.config.guild(ctx.guild).questions.set(questions)
                        await confirm.edit(content = "Domanda **modificata** con successo!")
                    else:
                        await confirm.edit(content = "Modifica della domanda **annullata** con successo!", embed = None)
                    await confirm.clear_reactions()
                else:
                    await msg.delete()
                    await ctx.message.add_reaction("🚫")
            except asyncio.TimeoutError:
                await msg.delete()
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
            await msg.add_reaction("✅")
            await msg.add_reaction("❎")
            def reaction_check(reaction, user):
                return user.id == ctx.message.author.id and ["✅", "❎"].count(str(reaction.emoji)) > 0 and reaction.message.id == msg.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check, timeout=60.0)        
                if str(reaction.emoji) == "✅":
                    questions.remove(question)
                    await self.config.guild(ctx.guild).questions.set(questions)
                    await msg.delete()
                    await ctx.message.add_reaction("✅")
                else:
                    await msg.delete()
                    await ctx.message.add_reaction("🚫")
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.message.add_reaction("🚫")
                            
    @trivia.command(aliases = ["db"])
    async def list(self, ctx: commands.Context, value: int = None):
        """Visualizzare la lista delle domande"""
        if role_check(ctx, [659513332218331155, 454268394464870401, 454262524955852800, 720221658501087312, 659513332218331155]):
            questions = await self.config.guild(ctx.guild).questions()
            setup = await self.config.guild(ctx.guild).setup()
            hex_int = int(setup["color"].replace("#", "0x"), 16)
            if len(questions) < 1:
                await ctx.send(content = "Non riesco a trovare **domande memorizzate** nel database.\nPuoi utilizzare il comando **`?domanda`** per aggiungerne altre.")
            else:          
                if value is None:
                    embed = discord.Embed(title = "Lista Domande", description = "```?trivia lista <numero>```", color = hex_int)
                    embed.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
                    for n, el in enumerate(questions):
                        embed.add_field(name = f"Domanda {n + 1}", value = el['question'], inline = False)
                    await ctx.send(embed = embed)
                else:
                    question = questions[value - 1]
                    embed = await create_embed(self, question)
                    await ctx.send(content = f"Domanda **{value}** di {str(len(questions))}", embed = embed)
    
    @trivia.command(aliases = ["lb"])
    async def leaderboard(self, ctx: commands.Context):
        """Visualizzare la classifica in base alle risposte corrette"""
        if role_check(ctx, [454262524955852800, 454262403819896833, 454268394464870401]):
            score = await self.config.guild(ctx.guild).score()
            description = ""
            for n, el in enumerate(score):
                description += f"**{n + 1}.** {ctx.guild.get_member(int(el))} (`{score[el]}`)\n"
            description = listify(description)
            if len(description) > 1:
                i = 0
                msg = await ctx.send(embed = lb_embed(setup, description, i))
                for arrow in arrow_reactions:
                    await msg.add_reaction(arrow)

                def check(reaction, user):
                    return user == ctx.author
                reaction = None
                while True:
                    if str(reaction) == arrow_reactions[0]:
                        i = 0
                        embed = await lb_embed(self, description, i)
                        await message.edit(embed = embed)
                    elif str(reaction) == arrow_reactions[1]:
                        if i > 0:
                            i -= 1
                            embed = await lb_embed(self, description, i)
                            await message.edit(embed = embed)
                    elif str(reaction) == arrow_reactions[2]:
                        if i < len(description):
                            i += 1
                            embed = await lb_embed(self, description, i)
                            await message.edit(embed = embed)
                    elif str(reaction) == arrow_reactions[3]:
                        i = len(description)
                        embed = await lb_embed(self, description, i)
                        await message.edit(embed = embed)
                    elif str(reaction) == arrow_reactions[4]:
                        await message.clear_reactions()
                        break
                    
                    await message.remove_reaction(reaction.emoji, ctx.author)

                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout = 30.0, check = check)
                        await message.remove_reaction(reaction, user)
                    except:
                        break
                await message.clear_reactions()
                
            else:
                embed = await lb_embed(self, description, 0)
                await ctx.send(embed = embed)

    @commands.guild_only()
    @commands.command()
    async def domanda(self, ctx : commands.Context):
        allowed_roles = [659513332218331155, 454268394464870401, 454262524955852800, 720221658501087312, 659513332218331155]
        for n, role in enumerate(allowed_roles):
            role = ctx.guild.get_role(role)
            allowed_roles[n] = role
        if len(set(ctx.author.roles).intersection(set(allowed_roles))) > 0:
            q = await self.config.guild(ctx.guild).questions()
            if len(q) > 15:
                return await ctx.send("Il **limite massimo** per le domande è stato raggiunto!\nProva ad eliminarne qualcuna con il comando `?trivia remove`")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            await ctx.send("Qual è la **domanda**?")
            try:
                question = await self.bot.wait_for('message', check=check, timeout=300.0)
            except:
                return
            if len(question.content) > 256:
                return await ctx.send("La **lughezza massima** per la domanda (256 caratteri) è stata superata, riprovare!")
            
            await ctx.send("Qual è la **risposta corretta**?")
            try:
                correct_answer = await self.bot.wait_for('message', check=check, timeout=300.0)
            except:
                return

            await ctx.send("Scrivi ora le **risposte errate**, separate da una `,`.")
            try:
                incorrect_answers_raw = await self.bot.wait_for('message', check=check, timeout=300.0)
            except:
                return
            incorrect_answers = incorrect_answers_raw.content.split(",")
            for n, answer in enumerate(incorrect_answers):
                incorrect_answers[n] = answer.strip()
            question = {
                "question" : question.content,
                "correct_answer" : correct_answer.content,
                "incorrect_answers" : incorrect_answers
            }
            await ctx.send("Invia ora l'immagine come **allegato**, altrimenti rispondi `No`.")
            try:
                image = await self.bot.wait_for('message', check=check, timeout=300.0)
            except:
                return
            if image.attachments != []:
                format_check = image.attachments[0].filename.lower()
                if format_check.endswith((".png", ".jpg", ".jpeg", ".gif", ".tiff", ".bmp")) == True:
                    question.update({"image" : image.attachments[0].url})
                else:
                    return await ctx.send("L'immagine allegata non è un **formato valido**, riprovare!")

            await ctx.send("Quale sarà la **durata** del quiz? Usa il formato `HH:MM`.")
            try:
                time = await self.bot.wait_for('message', check=check, timeout=300.0)
            except:
                return
            time = time.content.split(":")
            try:
                for n, el in enumerate(time):
                    time[n] = int(time[n])
            except:
                return await ctx.send("Specifica un'orario nel **formato corretto** (`HH:MM`), riprovare!")
            question.update({"time" : time})
            
            embed = await create_embed(self, question)

            msg = await ctx.send(content = "Reagisci con <:FNIT_ThumbsUp:454640434380013599> per **aggiungere la domanda**.", embed = embed)
            await msg.add_reaction("<:FNIT_ThumbsUp:454640434380013599>")
            await msg.add_reaction("<:FNIT_ThumbsDown:454640434610700289>")
            
            def reaction_check(reaction, user):
                return user == ctx.message.author and (str(reaction.emoji) == "<:FNIT_ThumbsUp:454640434380013599>" or str(reaction.emoji) == "<:FNIT_ThumbsDown:454640434610700289>") and reaction.message.id == msg.id
            reaction, user = await self.bot.wait_for('reaction_add', check=reaction_check, timeout=60.0)
            if str(reaction.emoji) == "<:FNIT_ThumbsUp:454640434380013599>":
                questions = await self.config.guild(ctx.guild).questions()
                questions.append(question)
                await self.config.guild(ctx.guild).questions.set(questions)
                await msg.edit(content = "Domanda **aggiunta** con successo!")
            await msg.clear_reactions()
    
    #---------------# EVENT #---------------#
    
    @tasks.loop(seconds=10, count=1)
    async def start_post(self):
        guild = self.bot.get_guild(454261607799717888)
        setup = await self.config.guild(guild).setup()
        time = setup["time"]
        now = datetime.datetime.now()
        if now.hour < time:
            post_time = datetime.datetime(now.year, now.month, now.day, time)
        else:
            hop = now + datetime.timedelta(days = 1) - datetime.timedelta(hours = now.hour - time)
            post_time = datetime.datetime(hop.year, hop.month, hop.day, hop.hour)
        delta_time = post_time - now
        await sleep(delta_time.seconds)
        self.daily_post.start()
                            
    @tasks.loop(hours=24)
    async def daily_post(self):
        guild = self.bot.get_guild(454261607799717888)
        await close_post(self)
                            
    @tasks.loop(minutes=10)
    async def checker(self):
        # Check if questions ended
        guild = self.bot.get_guild(454261607799717888)
        reaction = await self.config.guild(guild).reaction()
        if datetime.datetime.fromtimestamp(reaction['time']) < datetime.datetime.now():
            await close(self)
                    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
        guild = self.bot.get_guild(454261607799717888)
        data = await self.config.guild(guild).reaction()
        if guild.get_member(payload.user_id).bot == False:
            if data["message"] == payload.message_id:
                if payload.user_id not in data["users"]:
                    if str(payload.emoji) in reactions:
                        #if reactions.index(str(payload.emoji)) == data["correct"]:
                            #update_db(guild.id, payload.user_id, 100)
                        users = data["users"]
                        users.append(payload.user_id)
                        data.update({"users" : users})
                        await self.config.guild(guild).reaction.set(data)
                msg = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await msg.remove_reaction(payload.emoji, guild.get_member(payload.user_id))
                
