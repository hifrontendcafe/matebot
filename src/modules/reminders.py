# -*- coding: utf-8 -*-

import os
import re
import logging
from enum import Enum
from datetime import datetime, timedelta

import dateparser
from discord import Embed, Colour
from discord.ext import commands
import zoneinfo

from libs.reminder_core import ReminderCore
from libs.database import Database as DB
from libs.embed import EmbedGenerator
from scripts.embeds_reminder import addressee_reminder, channel_reminder, create_reminder_embed, date_reminder, description_reminder, title_reminder, type_reminder


class Error(Enum):
    DATETIME        = 1
    TIMEZONE        = 2
    DATE_HAS_PASSED = 3
    CHANNEL         = 4

log = logging.getLogger(__name__)


class Reminders(commands.Cog):
    """
    ## Módulo Reminders

    Programa un recordatorio y da el aviso en:
    - Una fecha y hora exáctos (único aviso)
    - Cada semana/mes en un día exacto (periódicos)

    ### Comandos:

    `>reminder add`: Agrega un recordatorio mediante una serie de pasos

    `>reminder ls`: Lista los recordatorios creados

    `>reminder rm <id>`: Elimina un recordatorio dado un id

    `>reminder help`: Muestra un mensaje con los comandos en detalle
    """

    def __init__(self, bot):
        self.bot = bot
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.PREFIX = os.getenv("DISCORD_PREFIX")
        self.add_reminder = {
            "title": '',
            "description": "",
            "text": "",
            "channel": 0,
            "type": None,
            "day": "",
            "time": "",
            "date": "",
            "author_id": ""
        }

        if secret != None:
            self.db = DB(secret)
        self._reminder = ReminderCore(self.db)

        # Nombre de la colección de la DB
        self._reminder.collection = "Events"
        # Mapeo de indices utilizados
        self._reminder.indexes = {
            'by_id_and_author': 'event_by_id_and_author',
            'by_time': 'all_events_by_time',
            'all': 'all_events'
        }
        # Defino la función que se utiliza para ejecutar los eventos
        self._reminder.action = self.action

    @staticmethod
    def _process_date_time(date, time):
        date_time = dateparser.parse(f'le {date} {time} -03:00')
        tz = zoneinfo.ZoneInfo('America/Buenos_Aires')
        date_time_now = datetime.now(tz)
        if date_time is None:
            return Error.DATETIME
        elif date_time < date_time_now:
            return Error.DATE_HAS_PASSED
        else:
            return date_time

    @staticmethod
    def colour(colour_type: str) -> int:
        colour = {
            'ERROR': Colour.red().value,
            'INFO': Colour.blue().value,
            'WARNING': Colour.gold().value,
        }
        return colour[colour_type]

    @staticmethod
    def _process_author(author):
        match = re.search(r"\<\@(\!|.)(\d+)\>", author)
        if match == None:
            return None
        author_id = int(match.group(2))
        return author_id

    @staticmethod
    def _process_channel(channel):
        match = re.search(r"\<\#(\d+)\>", channel)
        if match:
            channel_id = int(match.group(1))
            return channel_id
        else:
            return Error.CHANNEL

    def _generate_list(self, docs):
        fields = []
        for doc in docs:
            title = f"📅 {doc['data']['content']['title']}"
            channel = f"**Canal**: <#{doc['data']['channel']}>"
            date, time, _ = doc['data']['str_time'].split(' | ')
            date = '-'.join(date.split('-')[::-1])
            date_time = f"**Fecha y Hora**: {date} {time}"
            author = f"**Autor**: <@!{doc['data']['author_id']}>"
            ref_id = f"**ID**: {doc['ref'].id()}"

            fields.append((
                title,
f"""
{channel} | {date_time}
{author} | {ref_id}
"""
            ))
        embed = Embed(title="Lista de recordatorios", color=self.colour(colour_type='INFO'))
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=False)
        return embed

    @staticmethod
    def _check_permisson(author, channel):
        permission = author.permissions_in(channel)
        return permission.send_messages

    async def action(self, msg, content, channel_id):
        e = EmbedGenerator()
        e.content = content
        embed = e.generate_embed()
        channel = self.bot.get_channel(int(channel_id))
        await channel.send(f"{msg}! <:fecimpostor:755971090471321651>", embed=embed)

    # Comandos del bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Reminders is on")
        await self._reminder.load()


    @commands.group()
    async def reminder(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send('Commando inválido ...')


    @reminder.command()
    async def add(self, ctx):
        """ Comando reminder add

        Agrega un nuevo evento y pograma los recordatorios.
        """

        log.info("Reminder add")

        def check_reaction(reaction, user):
            return ctx.author == user

        # Paso 1: Inicio de creación del recordatorio
        emoji_selection = await create_reminder_embed(ctx, self.bot)
        if emoji_selection == "❌":  return await ctx.send("👍")

        # Paso 2: Destinatarios del recordatorio
        text, author_id = await addressee_reminder(ctx, self.bot)
        self.add_reminder["text"] = text
        self.add_reminder["author_id"] = author_id

        # Paso 3: Nombre del recordatorio
        self.add_reminder["title"] = await title_reminder(ctx, self.bot)

        # Paso 4: Descripción del recordatorio
        self.add_reminder["description"] = await description_reminder(ctx, self.bot)

        # Paso 5: Canal de publicación del recordatorio
        self.add_reminder["channel"] = await channel_reminder(ctx, self.bot, self._process_channel, self.colour)

        # Paso 6: Recordatorio único o recurrente
        self.add_reminder["type"] = await type_reminder(ctx, self.bot)

        if self.add_reminder["type"] == "date":
        # Paso 7-date: Día y hora del recordatorio
            rem_date, rem_time = await date_reminder(ctx, self.bot, self._process_date_time, self.colour)
            self.add_reminder["date"] = rem_date
            self.add_reminder["time"] = rem_time

        # Paso final: Resumen
        e = EmbedGenerator()
        e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
        e.title = "[ADD] Agregar recordatorio"
        e.description = f"""
Perfecto! El recordatorio quedaría de la
siguiente manera:

**{self.add_reminder["title"]}**
{self.add_reminder["description"]}
{self.add_reminder["channel"]}
{self.add_reminder["date"]} {self.add_reminder["time"]}
{'__Recordatorio único__' if self.add_reminder["type"] == "date" else ''}
{'__Recordatorio semanal__' if self.add_reminder["type"] == "cron" else ''}
{'__Recordatorio mensual__' if self.add_reminder["type"] == "cron" else ''}
"""
        e.fields= [("Reacciones", """
✅ Se ve bien, crear evento!
❌ Nop, volveré a hacerlo
""")]
        embed = e.generate_embed()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(emoji="✅")
        await msg.add_reaction(emoji="❌")
        reaction, _ = await self.bot.wait_for('reaction_add', check=check_reaction)
        await msg.delete()
        if reaction.emoji == "❌":
            return await ctx.send("❌ Creación de recordatorio cancelado!")
        else:
            author = self.bot.get_user(self.add_reminder["author_id"])
            date_time = dateparser.parse(f'le {self.add_reminder["date"]} {self.add_reminder["time"]} -03:00')
            if date_time == None:
                return
            channel_id = self._process_channel(self.add_reminder["channel"])

            e.title = f"[Recordatorio] {self.add_reminder['title']}"
            e.description = self.add_reminder['description']
            e.fields = [("Matetip <:fecmate:960390626954854441>", f"Con el comando `{self.PREFIX}reminder help` puedes ver todos los comandos para recordatorios")]
            embed = e.generate_embed()
            content = e.content

            print(content)
            doc = {}
            if self.add_reminder["type"] == "date":
                doc = await self._reminder.add_date(
                    author=author,
                    channel=str(channel_id),
                    content=content,
                    message=text,
                    time=date_time
                )
                log.info(f'Doc Fauna: {doc}')
            if doc != {}:
                e.title = f"Recordatorio creado!"
                e.description = "Guarda el ID para poder borrar el recordatorio en cualquier momento"
                e.fields = [(
                    "ID del recordatorio", doc['ref'].id()
                )]
                embed = e.generate_embed()
                await ctx.send(embed=embed) # Send embed to channel
            try:
                await author.send(embed=embed) # Send embed to author by DM
            except Exception:
                pass

    @reminder.command(aliases=["ls"])
    async def list(self, ctx):
        """ Comando `>reminder list`

        Muestra todos los recordatorios programados que están vigentes.
        """

        log.info("Reminder list")
        docs = await self._reminder.list()
        # Recibo la lista de ventos
        if docs:
            embed = self._generate_list(docs)
            await ctx.send(embed=embed, delete_after=60)
        else:
            embed = Embed(title="🟨 Lista Vacía", color=self.colour(colour_type='WARNING'))
            await ctx.send(embed=embed, delete_after=60)


    @reminder.command(aliases=["rm"])
    async def remove(self, ctx, id_: str):
        """ Comando `>reminder remove`

        Elimina un recordatorio programado.
        Solo el propietario del evento puede removerlo.
        """

        log.info("Reminder remove")
        doc = await self._reminder.remove(id_, str(ctx.author))
        if doc:
            title = f"📆 {doc['data']['content']['title']}"
            channel = f"**Canal**: <#{doc['data']['channel']}>"
            date, time, _ = doc['data']['str_time'].split(' | ')
            date = '-'.join(date.split('-')[::-1])
            date_time = f"**Fecha y Hora**: {date} {time}"
            author = f"**Autor**: <@!{doc['data']['author_id']}>"
            ref_id = f"**ID**: {doc['ref'].id()}"

            field = [
                title,
f"""
{channel} | {date_time}
{author} | {ref_id}
"""
            ]
            embed = Embed(title="🟦 Recordatorio eliminado", color=self.colour(colour_type='INFO'))
            embed.add_field(name=field[0], value=field[1], inline=False)
            await ctx.send(embed=embed, delete_after=60)
        else:
            embed = Embed(title="🟨 ID no encontrado o no eres el propiteario del evento", color=self.colour(colour_type='WARNING'))
            await ctx.send(embed=embed, delete_after=60)


    @reminder.command()
    async def help(self, ctx):
        """ Comando `>reminder help`

        Muestra la ayuda.
        """

        log.info("Reminder Help")
        PREFIX = os.getenv("DISCORD_PREFIX")

        h = EmbedGenerator()
        h.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
        h.title = f"Ayuda del comando: `reminder`"
        h.description = ""
        h.fields = [
            (f"`{PREFIX}reminder add`", "Programa un nuevo recordatorio."),
            (f"`{PREFIX}reminder list` o `{PREFIX}reminder ls`", "Lista los recordatorios programados."),
            (f"`{PREFIX}reminder remove ID` o `{PREFIX}reminder rm ID`", "Elimina un recordatorio programado."),
            (f"`{PREFIX}reminder help`", "Muestra la ayuda.")
        ]
        embed = h.generate_embed()
        return await ctx.send(embed=embed, delete_after=60)
