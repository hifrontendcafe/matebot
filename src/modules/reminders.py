# -*- coding: utf-8 -*-

import os
import re
import logging
import asyncio
from datetime import datetime, timezone, timedelta

import dateparser
from discord import Embed, Colour
from discord.ext import commands

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
    """ Módulo Scheduler

    Programa un evento y da aviso con las siguientes frecuencias:
    - 1 día antes
    - 1 hora antes
    - 10 minutos antes

    Comandos:
        >sched add <datetime> | <channel> | <content>
        >sched list ó >sched ls
        >sched remove <id> ó >sched rm <id>
        >sched help

    Ejemplo:
        >sched add hoy a las 22:00 gmt-3 | #channel | Mi evento
        >sched add el 2030/12/24 a las 8pm gmt-3 | #channel | Mi evento
        >sched remove 12345
    """

    def __init__(self, bot):
        self.bot = bot
        secret = os.getenv("FAUNADB_SECRET_KEY")


        self.reminder = Reminder(secret)

        # Nombre de la colección de la DB
        self.reminder.collection = "Events"
        # Mapeo de indices utilizados
        self.reminder.indexes = {
            'by_id_and_author': 'event_by_id_and_author',
            'by_time': 'all_events_by_time',
            'all': 'all_events'
        }
        # Defino la función que se utiliza para ejecutar los eventos
        self.reminder.action = self.action
        # Defino los recodatorios
        self.reminder.reminders = [
            {"delta": timedelta(days=1),     "message": "_**Mañana comenzamos, te esperamos!!**_"},
            {"delta": timedelta(hours=1),    "message": "_**Nos estamos preparando, en 1 hora arrancamos!!**_"},
            {"delta": timedelta(minutes=10), "message": "_**En 10 minutos arrancamos, no te lo pierdas!!**_"}
        ]

        self.emoji = {
            'OK': "\N{BALLOT BOX WITH CHECK}\N{VARIATION SELECTOR-16}",
            'CANCEL': "\N{NO ENTRY SIGN}"
        }


    @staticmethod
    def colour():
        # green: 0x00c29d
        # red: 0xe62f48
        return Colour.purple().value


    @staticmethod
    def _process_text(text):
        result = " ".join(text)
        result = [x.strip() for x in result.split("|", 2)]
        if len(result) == 3:
            date_time, channel, content = result[0], result[1], result[2]
            return date_time, channel, content
        else:
            return None, None, None


    @staticmethod
    def _process_date_time(date_time):
        date_time = dateparser.parse(date_time)
        date_time_now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if date_time is None:
            return Error.DATETIME
        elif date_time.strftime("%z") is "":
            return Error.TIMEZONE
        elif date_time < date_time_now:
            return Error.DATE_HAS_PASSED
        else:
            return date_time

    @staticmethod
    def _process_author(author):
        match = re.search(r"\<\@(\!|.)(\d+)\>", author)
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
        author = ""
        date_time = ""
        ref_id = ""
        for doc in docs:
            author += "<@!{}>\n".format(doc['data']['author_id'])
            date_time += "{}\n".format(doc['data']['str_time'])
            ref_id += "{}\n".format(doc['ref'].id())

        fields = [
            ("Author", author),
            ("Fecha", date_time),
            ("ID", ref_id),
        ]
        embed = Embed(title="Lista de eventos", color=self.colour())
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=True)
        return embed


    def _generate_next(self, doc):
        author = "<@!{}>\n".format(doc['data']['author_id'])
        date_time = "{}\n".format(doc['data']['str_time'])
        ref_id = "{}\n".format(doc['ref'].id())

        fields = [
            ("Author", author),
            ("Fecha", date_time),
            ("ID", ref_id),
        ]

        description = doc['data']['content']
        embed = Embed(title="Próximo evento", description=description, color=self.colour())
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=True)
        return embed


    @staticmethod
    def _check_permisson(author, channel):
        permission = author.permissions_in(channel)
        return permission.send_messages


    async def action(self, msg, content, channel_id):
        channel = self.bot.get_channel(int(channel_id))
        await channel.send(f"{msg}\n\n{content}")


    # Comandos del bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Reminders is on")
        await self.reminder.load()


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

        # Paso 1: Inicio de creación del recordatorio
        e = EmbedGenerator(ctx)
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
        await ctx.send(embed=embed)

        # Paso 2: Nombre del recordatorio
        e.description = ""
        e.fields= [("¿Nombre del recordatorio?", """
En lo posible, debe ser corto y descriptivo.
Escribe el mensaje y aprieta <Enter>     
""")]
        embed = e.generate_embed()
        await ctx.send(embed=embed)

        # Paso 3: Descripción del recordatorio
        e.fields= [("¿Descripción del recordatorio?", """
Puede ser más largo, hasta 256 caractéres.
Escribe el mensaje y aprieta <Enter> 
""")]
        embed = e.generate_embed()
        await ctx.send(embed=embed)

        # Paso 4: Canal de publicación del recordatorio
        e.fields= [("¿En cuál canal publicar el recordatorio?", """
Presiona # y acontinuación el nombre del canal.
Escribe el mensaje y aprieta <Enter>
""")]
        embed = e.generate_embed()
        await ctx.send(embed=embed)

        # Paso 5: Recordatorio único o recurrente
        e.fields= [
            ("¿El recordatorio es único?", "Elije una opción"),
            ("Reacciones", """
1️⃣ Debe publicarse en una fecha exacta (será único)
2️⃣ Se repite un día en específico cada semana
3️⃣ Se repite un día en específico cada quincena
4️⃣ Se repite un día en específico cada mes
""")
        ]
        embed = e.generate_embed()
        await ctx.send(embed=embed)

        # Paso a6: Día y hora del recordatorio
        e.fields= [("¿Día y hora del recordatorio?", """
El formato a seguir es: dd/mm/yyyy HH:MM
Ejemplo: 28/01/2022 19:13
Escribe el mensaje y aprieta <Enter>
""")]
        embed = e.generate_embed()
        await ctx.send(embed=embed)

        # Paso final: Día y hora del recordatorio
        e.description = """
Perfecto! El recordatorio quedaría de la
siguiente manera:

<Nombre>
<Descripción laaaaaaaaaaaaaaaaaaaaaaaaarga>
<#Canal>
<Día> <Hora>
<Único || Semanal || Quincenal || Mensual>
"""
        e.fields= [("Reacciones", """
✅ Se ve bien, crear evento!
❌ Nop, volveré a hacerlo
""")]
        embed = e.generate_embed()
        await ctx.send(embed=embed)

        # date_time, channel, content = self._process_text(text)
        # if date_time is None or channel is None or content is None:
        #     embed = Embed(
        #         title="Error: parámetros incorrectos",
        #         description="Por favor, separe el contentido de esta manera: **<datetime> | <channel> | <content>**",
        #         color=self.colour()
        #     )
        #     return await ctx.send(embed=embed, delete_after=60)

        # # Verifico si la fecha fue parseada con exito
        # date_time = self._process_date_time(date_time)
        # if date_time is Error.DATETIME:
        #     embed = Embed(
        #         title="Error: fecha y hora",
        #         description="Por favor, expecifique con mas detalles la fecha del evento.",
        #         color=self.colour()
        #     )
        #     return await ctx.send(embed=embed, delete_after=60)
        # elif date_time is Error.TIMEZONE:
        #     embed = Embed(
        #         title="Error: zona horaria",
        #         description="Por favor, defina la zona horaria, por ejemplo `gmt-3`.",
        #         color=self.colour()
        #     )
        #     return await ctx.send(embed=embed, delete_after=60)
        # elif date_time is Error.DATE_HAS_PASSED:
        #     embed = Embed(
        #         title="Error: fecha pasada",
        #         description="Por favor, defina una fecha y hora posterior a la actual.",
        #         color=self.colour()
        #     )
        #     return await ctx.send(embed=embed, delete_after=60)

        # # Verifico el formato del channel
        # channel_id = self._process_channel(channel)
        # if channel_id is Error.CHANNEL:
        #     embed = Embed(
        #         title="Error",
        #         description="Por favor, elija un canal válido.",
        #         color=self.colour()
        #     )
        #     return await ctx.send(embed=embed, delete_after=60)

        # # Verifico que el author tenga pemisos para escribir en el canal objetivo
        # if self._check_permisson(ctx.author, ctx.bot.get_channel(channel_id)) is False:
        #     embed = Embed(
        #         title="Error de permisos",
        #         description="Ups lo siendo, necesita permisos para enviar mensajes a ese canal.",
        #         color=self.colour()
        #     )
        #     return await ctx.send(embed=embed, delete_after=60)

        # fields = [
        #     ("Usuario", "<@!{}>".format(ctx.author.id)),
        #     ("Fecha", date_time.strftime("%Y-%m-%d | %H:%M | %z")),
        #     ("Canal", "<#{}>".format(channel_id))
        # ]

        # embed = Embed(
        #     title="Confirmación del evento",
        #     description=content,
        #     color=self.colour()
        # )
        # for field in fields:
        #     embed.add_field(name=field[0], value=field[1], inline=True)
        # embed.set_footer(text="Los datos son correctos?")

        # msg = await ctx.send(embed=embed, delete_after=60)
        # await msg.add_reaction(self.emoji['CANCEL'])
        # await msg.add_reaction(self.emoji['OK'])


    # @sched.command(aliases=["ls"])
    # async def list(self, ctx):
    #     """ Comando sched list

    #     Muestra todos los eventos programados que están vigentes.
    #     """

    #     log.info("Scheduler list")

    #     # Recivo la lista de ventos
    #     docs = await self.reminder.list()
    #     if docs:
    #         embed = self._generate_list(docs)
    #         await ctx.send(embed=embed, delete_after=60)
    #     else:
    #         embed = Embed(title="Lista Vacía")
    #         await ctx.send(embed=embed, delete_after=60)


    # @sched.command()
    # async def next(self, ctx):
    #     """ Comando sched next

    #     Muestra datos del próximo evento.
    #     """

    #     log.info("Scheduler next")

    #     # Recivo la lista de ventos
    #     docs = await self.reminder.list()
    #     if docs:
    #         embed = self._generate_next(docs[0])
    #         await ctx.send(embed=embed, delete_after=60)
    #     else:
    #         embed = Embed(title="Sin eventos", color=self.colour())
    #         await ctx.send(embed=embed, delete_after=60)


    # @sched.command(aliases=["rm"])
    # async def remove(self, ctx, id_: str):
    #     """ Comando sched remove

    #     Elimina un evento programado.
    #     Solo el propietario del evento puede removerlo.
    #     """

    #     log.info("Scheduler remove")
    #     doc = await self.reminder.remove(id_, str(ctx.author))
    #     if doc:
    #         fields = [
    #             ("Usuario", "<@!{}>".format(doc['data']['author_id'])),
    #             ("Fecha", doc['data']['str_time']),
    #             ("ID", str(doc['ref'].id()))
    #         ]
    #         embed = Embed(title="Evento eliminado", color=self.colour())
    #         for field in fields:
    #             embed.add_field(name=field[0], value=field[1], inline=True)
    #         await ctx.send(embed=embed, delete_after=60)
    #     else:
    #         embed = Embed(title="ID no encontrado o no eres el propiteario del evento", color=self.colour())
    #         await ctx.send(embed=embed, delete_after=60)


    # @sched.command()
    # async def clear_dm(self, ctx):
    #     messages_to_remove = 10

    #     async for message in self.bot.get_user(ctx.author.id).history(limit=messages_to_remove):
    #         if message.author.id == self.bot.user.id:
    #             await message.delete()
    #             await asyncio.sleep(1)


    # @sched.command()
    # async def help(self, ctx):
    #     """ Comando sched help

    #     Muestra la ayuda.
    #     """

    #     log.info("Scheduler Help")
    #     PREFIX = os.getenv("DISCORD_PREFIX")

    #     author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    #     title = f"Ayuda del comando: `sched`"
    #     fields = [
    #         (f"{PREFIX}sched add", "Programa un nuevo evento."),
    #         (f"{PREFIX}sched list | ls", "Lista los eventos pendientes."),
    #         (f"{PREFIX}sched next", "Información del próximo evento."),
    #         (f"{PREFIX}sched remove | rm", "Elimina un evento programado."),
    #         (f"{PREFIX}sched help", "Muestra la ayuda."),
    #         ("Ejemplos:",
    #             f"""
    #             {PREFIX}sched add <datetime> | <channel> | <content>\n\
    #             {PREFIX}sched add mañana a las 22:00 gmt-3 | #my-channel | https://google.com\n\
    #             {PREFIX}sched list\n\
    #             {PREFIX}sched remove <id>\n\
    #             {PREFIX}sched rm 281547393529283072
    #             """
    #         )
    #     ]

    #     embed = Embed(title=title, color=self.colour())
    #     embed.set_author(name=author[0], icon_url=author[1])
    #     for field in fields:
    #         embed.add_field(name=field[0], value=field[1], inline=False)
    #     return await ctx.send(embed=embed, delete_after=60)


    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     # Obtain reactioned message by id
    #     channel = self.bot.get_channel(payload.channel_id)
    #     msg = await channel.fetch_message(payload.message_id)
    #     # Check if reactined message was sended by the bot
    #     colour = msg.embeds[0].colour if len(msg.embeds) == 1 else Embed.Empty
    #     if colour != Embed.Empty:
    #         colour = colour.value
    #     if msg.author == self.bot.user and colour == self.colour():
    #         # Check if the reaction was added by the bot
    #         if payload.user_id != self.bot.user.id:
    #             if payload.emoji.name == self.emoji['OK']:
    #                 # Recovery data from message
    #                 fields = msg.embeds[0].fields
    #                 str_author = fields[0].value
    #                 str_date_time = fields[1].value
    #                 str_channel = fields[2].value
    #                 author_id = self._process_author(str_author)

    #                 author = self.bot.get_user(author_id)
    #                 date_time = datetime.strptime(str_date_time, "%Y-%m-%d | %H:%M | %z")
    #                 channel_id = self._process_channel(str_channel)
    #                 content = msg.embeds[0].description

    #                 PREFIX = os.getenv("DISCORD_PREFIX")

    #                 doc = await self.reminder.add(author, date_time, str(channel_id), content)
    #                 await msg.delete()
    #                 embed = Embed(
    #                     title="Evento agregado con exito!",
    #                     description=f"Puede ver sus eventos programados con:\n`{PREFIX}sched list`",
    #                     color=self.colour()
    #                 )
    #                 embed.set_footer(text=f"ID: {doc['ref'].id()}")
    #                 return await channel.send(embed=embed, delete_after=60)

    #             if payload.emoji.name == self.emoji['CANCEL']:
    #                 await msg.delete()
    #                 embed = Embed(title="Evento cancelado", color=self.colour())
    #                 return await channel.send(embed=embed, delete_after=60)
