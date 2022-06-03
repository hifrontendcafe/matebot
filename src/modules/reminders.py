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
from scripts.embeds_reminder import *


class Error(Enum):
    """Enumeración de errores."""
    DATETIME        = 1
    TIMEZONE        = 2
    DATE_HAS_PASSED = 3
    CHANNEL         = 4

DAYS = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

log = logging.getLogger(__name__)


class Reminders(commands.Cog):
    """
    ## Módulo Reminders

    Programa un recordatorio y da el aviso en:
    - Una fecha y hora exáctos (único aviso)
    - Cada semana/mes en un día exacto (periódicos)

    ### Comandos:

    `>reminder add`: Agrega un recordatorio mediante una serie de pasos

    `>reminder ls`: Lista los recordatorios creados por autor

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
            'by_author': 'events_by_author',
            'all': 'all_events',
        }
        # Defino la función que se utiliza para ejecutar los eventos
        self._reminder.action = self.action

    @staticmethod
    def _process_date_time(date, time):
        """
        Parseo de fecha y hora. Si hay un error con el formato o la fecha es anterior a la actual, lanza error.
        """
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
        """
        Genera un color de acuerdo a un tipo de color.
        """
        colour = {
            'ERROR': Colour.red().value,
            'INFO': Colour.blue().value,
            'WARNING': Colour.gold().value,
        }
        return colour[colour_type]

    @staticmethod
    def _process_author(author):
        """
        Parsea el autor de un recordatorio para obtener su id.
        """
        match = re.search(r"\<\@(\!|.)(\d+)\>", author)
        if match == None:
            return None
        author_id = int(match.group(2))
        return author_id

    @staticmethod
    def _process_channel(channel):
        """
        Parsea el canal de un recordatorio para obtener su id.
        """
        match = re.search(r"\<\#(\d+)\>", channel)
        if match:
            channel_id = int(match.group(1))
            return channel_id
        else:
            return Error.CHANNEL

    def _generate_list(self, docs):
        """
        Genera una lista de recordatorios a partir de los docs de FaunaDB.
        """
        fields = []
        for doc in docs:
            data = doc['data']
            description = data['content']['description']
            if len(description) > 150:
                description = description[:150] + " ..."
            title = f"📅 {data['content']['title']}"
            channel = f"**Canal**: <#{data['channel']}>"
            if data['type'] == 'date':
                date, time, _ = data['str_time'].split(' | ')
                date = '-'.join(date.split('-')[::-1])
                date_time = f"**Fecha y Hora**: {date} {time}"
            else:
                if "day" in data['cron']:
                    date_time = f"Cada día {data['cron']['day']} (mensual). "
                else:
                    date_time = f"Cada {DAYS[data['cron']['day_of_week']]} (semanal). "
                date_time += f"**Hora**: {data['cron']['hour']}:{data['cron']['minute']}"
            author = f"**Autor**: <@!{data['author_id']}>"
            ref_id = f"**ID**: {doc['ref'].id()}"

            fields.append((
                title,
f"""
{description}
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
        """
        Chequea si el usuario tiene permisos para crear recordatorios en el canal.
        """
        permission = author.permissions_in(channel)
        return permission.send_messages

    async def action(self, msg, content, channel_id):
        """
        Action callback que se ejecuta a la hora y fecha de un recordatorio. Envía un embed con el recordatorio.
        """
        e = EmbedGenerator()
        e.content = content
        embed = e.generate_embed()
        channel = self.bot.get_channel(int(channel_id))
        await channel.send(f"{msg}! <:fecimpostor:755971090471321651>", embed=embed)

    # Comandos del bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener que se ejecuta cuando el bot se conecta a Discord.
        """
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

        Agrega un nuevo evento y pograma los recordatorios. Estos pueden ser de tipo:
        - Una fecha y hora exactos (único aviso)
        - Cada semana/mes en un día exacto (periódicos)
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
        self.add_reminder["type"], is_cron_weekly = await type_reminder(ctx, self.bot)

        # Paso 7-date: Día y hora del recordatorio
        if self.add_reminder["type"] == "date":
            rem_date, rem_time = await date_reminder(ctx, self.bot, self._process_date_time, self.colour)
            self.add_reminder["date"] = rem_date
            self.add_reminder["time"] = rem_time
            date_time = dateparser.parse(f'le {self.add_reminder["date"]} {self.add_reminder["time"]} -03:00')

        # Paso 7-cron-a: Día de la semana y hora del recordatorio
        if self.add_reminder["type"] == "cron" and is_cron_weekly:
            # end_date = await end_reminder(ctx, self.bot, self._process_date_time, self.colour)
            day_of_week = await get_day_week(ctx, self.bot)
            hour, minute = await get_time(ctx, self.bot, self.colour)
            self.add_reminder["cron"] = {
                "day_of_week": day_of_week, # If semanal: monday, tuesday, wednesday, thursday, friday, saturday or sunday
                "hour": hour, # hour (0-23)
                "minute": minute, # minute (0-59)
                # "end_date": dateparser.parse(f'le {end_date} {rem_time}'),
                # "timezone": zoneinfo.ZoneInfo('America/Buenos_Aires')
            }

        if self.add_reminder["type"] == "cron" and (not is_cron_weekly):
            # end_date = await end_reminder(ctx, self.bot, self._process_date_time, self.colour)
            day = await get_day(ctx, self.bot, self.colour)
            hour, minute = await get_time(ctx, self.bot, self.colour)
            self.add_reminder["cron"] = {
                "day": day, # If monthly, day of the month (1-31)
                "hour": hour, # hour (0-23)
                "minute": minute, # minute (0-59)
                # "end_date": dateparser.parse(f'le {end_date} {rem_time}'),
                # "timezone": zoneinfo.ZoneInfo('America/Buenos_Aires')
            }

        # Paso final: Resumen
        date_reminder_embed = ""
        if self.add_reminder["type"] == "date":
            date_reminder_embed = f"**Fecha y hora**: {self.add_reminder['date']} {self.add_reminder['time']}"
        if self.add_reminder["type"] == "cron":
            date_reminder_embed = f"**Hora**: {self.add_reminder['cron']['hour']}:{self.add_reminder['cron']['minute']}"
        
        reminder_type = ""
        if self.add_reminder["type"] == "date":
            reminder_type = "__Recordatorio único__"
        if self.add_reminder["type"] == "cron":
            if is_cron_weekly:
                reminder_type = "__Recordatorio semanal__"
            else:
                reminder_type = "__Recordatorio mensual__"

        e = EmbedGenerator()
        e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
        e.title = "[ADD] Agregar recordatorio"
        e.description = f"""
Perfecto! El recordatorio quedaría de la
siguiente manera:

**{self.add_reminder["title"]}**
{self.add_reminder["description"]}
{self.add_reminder["channel"]}
{date_reminder_embed}
{reminder_type}
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
            channel_id = self._process_channel(self.add_reminder["channel"])

            e.title = f"{self.add_reminder['title']}"
            e.description = self.add_reminder['description']
            e.fields = [("Matetip <:fecmate:960390626954854441>", f"Con el comando `{self.PREFIX}reminder help` puedes ver todos los comandos para recordatorios")]
            embed = e.generate_embed()
            content = e.content

            doc = {}
            if self.add_reminder["type"] == "date":
                date_time = dateparser.parse(f'le {self.add_reminder["date"]} {self.add_reminder["time"]} -03:00')
                if date_time == None:
                    return
                doc = await self._reminder.add_date(
                    author=author,
                    channel=str(channel_id),
                    content=content,
                    message=text,
                    time=date_time
                )
                log.info(f'Doc Fauna: {doc}')

            if self.add_reminder["type"] == "cron":
                doc = await self._reminder.add_cron(
                    author=author,
                    channel=str(channel_id),
                    content=content,
                    message=text,
                    cron=self.add_reminder["cron"]
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
        author = str(self.bot.get_user(ctx.message.author.id))
        docs = await self._reminder.list(author=author)
        # Recibo la lista de ventos por DM (si está bloqueado, lo mando al canal)
        if docs:
            embed = self._generate_list(docs)
            message = f"Hola {ctx.author.mention}! Aquí están todos los recordatorios que tienes programados:"
            try:
                await ctx.message.author.send(message)
                await ctx.message.author.send(embed=embed)
            except:
                await ctx.send(message, delete_after=60)
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
            data = doc['data']
            title = f"📅 {data['content']['title']}"
            channel = f"**Canal**: <#{data['channel']}>"
            if data['type'] == 'date':
                date, time, _ = data['str_time'].split(' | ')
                date = '-'.join(date.split('-')[::-1])
                date_time = f"**Fecha y Hora**: {date} {time}"
            else:
                if "day" in data['cron']:
                    date_time = f"Cada día {data['cron']['day']} (mensual). "
                else:
                    date_time = f"Cada {DAYS[data['cron']['day_of_week']]} (semanal). "
                date_time += f"**Hora**: {data['cron']['hour']}:{data['cron']['minute']}"
            author = f"**Autor**: <@!{data['author_id']}>"
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
