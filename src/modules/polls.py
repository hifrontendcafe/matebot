# Modulo polls.py v1

# ///---- Imports ----///
import re
import os
import logging

import discord
from discord.ext.commands import Cog, has_permissions, group, MissingPermissions

# Database
from libs.database import Database as DB

# ///---- Log ----///
log = logging.getLogger(__name__)


# ///---- Clase ----///
class Polls(Cog):
    '''
    Creación de polls
    '''

    def __init__(self, bot):
        '''
        __init__ del bot (importa este codigo como modulo al bot)
        '''
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.bot = bot
        self.db = DB(secret)

    #! !poll
    #! Comando poll
    @group()
    async def poll(self, ctx):
        '''
        Comando !poll
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send("Este comando no existe! Tipea `!poll help` para ver los comandos disponibles :D")

    #! Subcomando help
    @poll.command()
    async def help(self, ctx):
        '''
        Descripción: Ayuda de Encuestas
        Precondicion: Escribir en un canal !poll help
        Poscondición: El bot escribe lista de comandos con descripción
        '''
        PREFIX = os.getenv("DISCORD_PREFIX")
        lines = f"""
                ```md
### COMANDO {PREFIX}poll ###

- {PREFIX}poll help: Muestra la ayuda.
- {PREFIX}poll add: Agregar encuesta.
- {PREFIX}poll close: Finalizar encuesta.

Ejemplos:
{PREFIX}poll add "Pregunta" -> (Encuesta simple, Sí o No)
{PREFIX}poll add "¿Te gusta la comunidad de FrontendCafé?"

{PREFIX}poll add "Pregunta" "Opción 1" "Opción 2" "Opción 3" (Encuesta personalizada, máximo 10 respuestas)
{PREFIX}poll add "¿Participas de alguno de los grupos de estudio, cuál?" "Python-Study-Group" "JS-Study-Group" "PHP-Study-Group" "Algorithms-Group"

{PREFIX}poll close ID
{PREFIX}poll close 123456789654687651233
```
            """
        await ctx.send(lines)

    #! Subcomando add
    @poll.command()
    @has_permissions(manage_messages=True)
    async def add(self, ctx, question, *args):
        '''
        Agregar poll
        '''

        def db_create(self, id, poll_type, author, avatar, question, votes):
            self.db.create('Polls', {
                "id": id,
                "type": poll_type,
                "author": str(author),
                "avatar_url": str(avatar),
                "question": question,
                "is_active": True,
                "users_voted": [],
                "votes_count": votes
            })
        PREFIX = os.getenv("DISCORD_PREFIX")
        try:
            await ctx.message.delete()
            # Embed message
            pollEmbed = discord.Embed(
                title=(f":clipboard: {question}"), color=60349)
            pollEmbed.set_thumbnail(
                url="https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png")
            pollEmbed.set_author(name="Encuesta")
            pollEmbed.set_footer(
                text=ctx.author, icon_url=ctx.author.avatar_url)
            # Verifies if no answers were provided, and creates a yes/no poll
            if not args:
                pollEmbed.add_field(
                    name="\u200b", value="**Opciones (voto único):**\n✅ Sí: 0  \n❎ No: 0", inline=False)
                msg = await ctx.channel.send(embed=pollEmbed)
                votes_count = {
                    'Si': 0,
                    'No': 0
                }

                # Add poll to database
                db_create(self, msg.id, "normal", ctx.author,
                          ctx.author.avatar_url, question, votes_count)

                # Add BOT reactions
                emojis = ['✅', '❎']
                for emoji in emojis:
                    await msg.add_reaction(emoji)
            # Verifies if the amount of answers provided are more than 1 and equal or less than 10
            elif (len(args) > 1) and (len(args) <= 10):
                emoji_number_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                                     "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
                try:
                    # Format and add answers to embed
                    poll_text = ""
                    for idx, answer in enumerate(args):
                        poll_text += (
                            f"\n{emoji_number_list[idx]} {answer}: 0")

                    pollEmbed.add_field(
                        name="**Opciones (voto único):**", value=poll_text, inline=False)

                    # Dict of answers for DB
                    votes_count = {}
                    for answer in args:
                        votes_count[answer] = 0

                    # Send poll message to discord
                    msg = await ctx.channel.send(embed=pollEmbed)

                    # Add poll to database
                    db_create(self, msg.id, "custom", ctx.author,
                              ctx.author.avatar_url, question, votes_count)

                    # Add BOT reactions
                    for i in range(len(args)):
                        await msg.add_reaction(emoji_number_list[i])
                except Exception as e:
                    print(e)
            else:
                await ctx.channel.send("❌Cantidad de respuestas no válidas (mínimo 2 respuestas | máximo 10 respuestas)", delete_after=15)

            user = self.bot.get_user(ctx.author.id)
            await user.send(f"Para cerrar la votación de la encuesta '{question}' usar el siguiente comando: \n``` {PREFIX}poll close {msg.id} ```")
        except Exception as e:
            print(e)

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.message.delete()
            await ctx.channel.send("No tienes permiso para crear encuestas :slight_frown:", delete_after=15)

    @poll.command()
    @has_permissions(manage_messages=True)
    async def close(self, ctx, poll_id):
        emoji_number_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                             "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        try:
            poll = self.db.get_poll_by_discord_id(int(poll_id))
            votes = poll['data']['votes_count']
            self.db.update_with_ref(
                poll['ref'],
                {
                    "is_active": False,
                }
            )
            # Send finish message
            pollEmbed = discord.Embed(
                title=f":clipboard: {poll['data']['question']}", color=60349)
            pollEmbed.set_thumbnail(
                url="https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png")
            pollEmbed.set_author(name="Encuesta Finalizada")
            pollEmbed.set_footer(
                text=poll['data']['author'], icon_url=poll['data']['avatar_url'])

            poll_text = ""
            # Sort votes by greater to lower
            for idx, (k, v) in enumerate(sorted(votes.items(), key=lambda vote: vote[1], reverse=True)):
                poll_text += (
                    f"\n{emoji_number_list[idx]} {k}: {v}")
            pollEmbed.add_field(
                name="\u200b", value=f"**Votos:**{poll_text}", inline=False)
            await ctx.message.delete()
            await ctx.channel.send(embed=pollEmbed)
        except Exception as e:
            print(e)

    @close.error
    async def close_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.message.delete()
            await ctx.channel.send("No tienes permiso para cerrar encuestas :slight_frown:", delete_after=15)

    # On poll reaction:
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Obtain reactioned message by id
        channel = self.bot.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        # Check if reactined message was sended by the bot
        if (msg.author == self.bot.user):
            # Check if the reaction was added by the bot
            if (payload.user_id != self.bot.user.id):
                # Search poll in DB
                try:
                    poll = self.db.get_poll_by_discord_id(payload.message_id)
                    ref = poll['ref']
                    is_active = poll['data']['is_active']
                    p_type = poll['data']['type']
                    users = poll['data']['users_voted']
                    votes = poll['data']['votes_count']
                    # Check if poll is "active"
                    if is_active:
                       # Check if user has voted
                        if (payload.user_id not in users):
                            users.append(payload.user_id)
                            # Check if poll type is "normal" (yes/no poll)
                            if (p_type == "normal"):
                                if(payload.emoji.name == '✅'):
                                    votes['Si'] += 1
                                elif(payload.emoji.name == '❎'):
                                    votes['No'] += 1

                                # Update users and votes to DB
                                try:
                                    self.db.update_with_ref(
                                        ref,
                                        {
                                            "users_voted": users,
                                            "votes_count": votes
                                        }
                                    )
                                except Exception as e:
                                    print(e)
                                # Edit message
                                pollEmbed = discord.Embed(
                                    title=f":clipboard: {poll['data']['question']}", color=60349)
                                pollEmbed.set_thumbnail(
                                    url="https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png")
                                pollEmbed.set_author(name="Encuesta")
                                pollEmbed.set_footer(
                                    text=poll['data']['author'], icon_url=poll['data']['avatar_url'])
                                pollEmbed.add_field(
                                    name="\u200b", value=f"**Opciones (1 voto disponible):**\n:white_check_mark: Sí: {votes['Si']} \n:negative_squared_cross_mark: No: {votes['No']}", inline=False)
                                await msg.edit(embed=pollEmbed)
                            # Check if poll type is "custom" (personalizated answers poll)
                            elif (p_type == "custom"):
                                emoji_number_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                                                     "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
                                for idx, emoji in enumerate(emoji_number_list):
                                    if (emoji == payload.emoji.name):
                                        listVotes = list(votes)
                                        votes[listVotes[idx]] += 1
                                        # Update users and votes to DB
                                        try:
                                            self.db.update_with_ref(
                                                ref,
                                                {
                                                    "users_voted": users,
                                                    "votes_count": votes
                                                }
                                            )
                                            # Edit and send brew install superfly/tap/flyctlmessage
                                            pollEmbed = discord.Embed(
                                                title=f":clipboard: {poll['data']['question']}", color=60349)
                                            pollEmbed.set_thumbnail(
                                                url="https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png")
                                            pollEmbed.set_author(
                                                name="Encuesta")
                                            pollEmbed.set_footer(
                                                text=poll['data']['author'], icon_url=poll['data']['avatar_url'])
                                            poll_text = ""
                                            for idx, answer in enumerate(votes):
                                                poll_text += (
                                                    f"\n{emoji_number_list[idx]} {answer}: {votes[listVotes[idx]]}")
                                            pollEmbed.add_field(
                                                name="**Opciones (1 voto disponible):**", value=poll_text, inline=False)
                                            await msg.edit(embed=pollEmbed)
                                        except Exception as e:
                                            print(e)
                        else:
                            # Send DM if the user has voted
                            user = self.bot.get_user(payload.user_id)
                            await user.send(f"Ya has votado en la encuesta '{poll['data']['question']}'")
                    else:
                        # Send DM if the poll has finished
                        user = self.bot.get_user(payload.user_id)
                        await user.send(f"La votación de la encuesta '{poll['data']['question']}' ha finalizado")
                except Exception as e:
                    print(e)
