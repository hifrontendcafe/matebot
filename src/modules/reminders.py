# -*- coding: utf-8 -*-

import os
import re
import logging
from datetime import datetime, timedelta

import dateparser
from discord import Embed, Colour
from discord.ext import commands
import pytz

from libs.reminder import Reminder
from libs.embed import EmbedGenerator

from enum import Enum

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
    - Cada semana/quincena/mes en un día exacto (periódicos)

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
            "type": 0,
            "day": "",
            "time": "",
            "date": "",
            "author_id": ""
        }

        self._reminder = Reminder(secret)

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
        # Defino los recodatorios
        self._reminder.reminders = []

    @staticmethod
    def _process_date_time(date, time):
        date_time = dateparser.parse(f'{date} {time} -03:00')
        tz = pytz.timezone('America/Buenos_Aires')
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
            title = f"📅 {doc['data']['content'][0]}"
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
        channel = self.bot.get_channel(int(channel_id))
        await channel.send(f"Hola {content[2]}! <:fecimpostor:755971090471321651>", embed=msg)

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
    # async def add(self, ctx, *text):
    async def add(self, ctx):
        """ Comando reminder add

        Agrega un nuevo evento y pograma los recordatorios.
        """

        log.info("Reminder add")
        e = EmbedGenerator(ctx)

        def check(msg):
            if ctx.author == msg.author:
                self.add_reminder["author_id"] = ctx.author.id
                return msg

        def check_reaction(reaction, user):
            return ctx.author == user

        # Paso 1: Inicio de creación del recordatorio
        e.title = "[ADD] Agregar recordatorio"
        e.description = """
Hola! A continuación, te pediré los datos necesarios para crear uno o varios recordatorios. Sigue los pasos con atención!

Antes de terminar, te mostraré el resultado final a modo de vista previa.
"""
        e.fields= [("Reacciones", """
✅ Ok, empecemos!
❌ Nop, lo haré en otro momento
""")]
        embed = e.generate_embed()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(emoji="✅")
        await msg.add_reaction(emoji="❌")
        reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction)
        await msg.delete()
        if reaction.emoji == "❌":
            await ctx.send("👍")
            return

        # Paso 2: Destinatarios del recordatorio
        e.description = ""
        e.fields= [("¿Destinatarios del recordatorio?", """
Puedes colocar menciones a users y/o roles del FrontendCafé. **No se verán dentro del embed!**
Escribe el mensaje y aprieta <Enter>
""")]
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        msg = await self.bot.wait_for('message', check=check)
        self.add_reminder["text"] = msg.content
        await msg_bot.delete()
        await msg.delete()

        # Paso 3: Nombre del recordatorio
        e.description = ""
        e.fields= [("¿Nombre del recordatorio?", """
En lo posible, debe ser corto y descriptivo.
Escribe el mensaje y aprieta <Enter>
""")]
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        msg = await self.bot.wait_for('message', check=check)
        self.add_reminder["title"] = msg.content
        await msg_bot.delete()
        await msg.delete()

        # Paso 4: Descripción del recordatorio
        e.fields= [("¿Descripción del recordatorio?", """
Puede ser más largo, hasta 256 caractéres.
Escribe el mensaje y aprieta <Enter>
""")]
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        msg = await self.bot.wait_for('message', check=check)
        self.add_reminder["description"] = msg.content
        await msg_bot.delete()
        await msg.delete()

        # Paso 5: Canal de publicación del recordatorio
        e.fields= [("¿En cuál canal publicar el recordatorio?", """
Presiona # y acontinuación el nombre del canal.
Escribe el mensaje y aprieta <Enter>
""")]
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        msg = await self.bot.wait_for('message', check=check)
        channel_check = self._process_channel(msg.content)
        if channel_check is Error.CHANNEL:
            embed = Embed(
                title="🟥 Error",
                description="Por favor, elija un canal válido.\nTipee `#nombre-del-canal`.",
                color=self.colour(colour_type='ERROR')
            )
            return await ctx.send(embed=embed, delete_after=60)
        self.add_reminder["channel"] = msg.content
        await msg_bot.delete()
        await msg.delete()

        # Paso 6: Recordatorio único o recurrente
        e.fields= [
            ("¿El recordatorio es único?", "Elije una opción"),
            ("Reacciones", """
1️⃣ Debe publicarse en una fecha exacta (será único)
~~2️⃣ Se repite un día en específico cada semana~~ (Próximamente)
~~3️⃣ Se repite un día en específico cada quincena~~ (Próximamente)
~~4️⃣ Se repite un día en específico cada mes~~ (Próximamente)
""")
        ]
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        # emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        emojis = ["1️⃣"]
        for emoji in emojis:
            await msg_bot.add_reaction(emoji=emoji)
        reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction)
        self.add_reminder["type"] = emojis.index(reaction.emoji)
        await msg_bot.delete()

        if self.add_reminder["type"] == 0:
        # Paso a7: Día y hora del recordatorio
            e.fields= [("¿Día y hora del recordatorio?", """
El formato a seguir es: dd/mm/yyyy HH:MM
Ejemplo: 28/01/2022 19:13
Escribe el mensaje y aprieta <Enter>
""")]
            try:
                embed = e.generate_embed()
                msg_bot = await ctx.send(embed=embed)
                msg = await self.bot.wait_for('message', check=check)
                rem_date, rem_time = msg.content.split(" ")
                date_time = self._process_date_time(date=rem_date, time=rem_time)
                if date_time is Error.DATETIME:
                    embed = Embed(
                        title="🟥 Error: Formato inválido",
                        description="""Por favor, expecifique con mas detalles la fecha del evento.
    Ejemplo: `07/02/2022 21:19`""",
                        color=self.colour(colour_type='ERROR')
                    )
                    return await ctx.send(embed=embed, delete_after=60)
                elif date_time is Error.DATE_HAS_PASSED:
                    embed = Embed(
                        title="🟥 Error: Fecha pasada",
                        description="""Por favor, defina una fecha y hora posterior a la actual.
    Recuerde que la hora está en GMT-3 (Zona horaria de Argentina)""",
                        color=self.colour(colour_type='ERROR')
                    )
                    return await ctx.send(embed=embed, delete_after=60)
                self.add_reminder["date"] = rem_date
                self.add_reminder["time"] = rem_time
                await msg_bot.delete()
                await msg.delete()
            except ValueError:
                embed = Embed(
                    title="🟥 Error: Formato inválido",
                    description="""Por favor, expecifique con mas detalles la fecha del evento.
Ejemplo: `07/02/2022 21:19`""",
                    color=self.colour(colour_type='ERROR')
                )
                return await ctx.send(embed=embed, delete_after=60)

        # Paso final: Resumen
        e.description = f"""
Perfecto! El recordatorio quedaría de la
siguiente manera:

**{self.add_reminder["title"]}**
{self.add_reminder["description"]}
{self.add_reminder["channel"]}
{self.add_reminder["date"]} {self.add_reminder["time"]}
{'__Recordatorio único__' if self.add_reminder["type"] == 0 else ''}
{'__Recordatorio semanal__' if self.add_reminder["type"] == 1 else ''}
{'__Recordatorio quincenal__' if self.add_reminder["type"] == 2 else ''}
{'__Recordatorio mensual__' if self.add_reminder["type"] == 3 else ''}
"""
        e.fields= [("Reacciones", """
✅ Se ve bien, crear evento!
❌ Nop, volveré a hacerlo
""")]
        embed = e.generate_embed()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(emoji="✅")
        await msg.add_reaction(emoji="❌")
        reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction)
        await msg.delete()
        if reaction.emoji == "❌":
            await ctx.send("👍")
            return
        else:
            author = self.bot.get_user(self.add_reminder["author_id"])
            date_time = dateparser.parse(f'{self.add_reminder["date"]} {self.add_reminder["time"]} -03:00')
            if date_time == None:
                return
            channel_id = self._process_channel(self.add_reminder["channel"])
            e.title = f"[Recordatorio] {self.add_reminder['title']}"
            e.description = self.add_reminder['description']
            e.fields = [("Pro tip", f"Con el comando `{self.PREFIX}reminder help` puedes ver todos los comandos para recordatorios")]
            embed = e.generate_embed()
            self._reminder.reminders = [
                {"delta": timedelta(minutes=1), "message": embed},
            ]
            doc = await self._reminder.add(
                author,
                date_time,
                str(channel_id),
                [
                    self.add_reminder["title"],
                    self.add_reminder["description"],
                    self.add_reminder["text"],
                    self.add_reminder["type"]
                ]
            )
            if doc != None:
                e.title = f"Recordatorio creado!"
                e.description = "Guarda el ID para poder borrar el recordatorio en cualquier momento"
                e.fields = [(
                    "ID del recordatorio", doc['ref'].id()
                )]
            embed = e.generate_embed()
            await ctx.send(embed=embed)
            try:
                await author.send(embed=embed)
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
            title = f"📆 {doc['data']['content'][0]}"
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

        h = EmbedGenerator(ctx)
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
