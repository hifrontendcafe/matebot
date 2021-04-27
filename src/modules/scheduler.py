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

from enum import Enum

class Error(Enum):
    DATETIME        = 1
    TIMEZONE        = 2
    DATE_HAS_PASSED = 3
    CHANNEL         = 4

log = logging.getLogger(__name__)


class Scheduler(commands.Cog):
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
        # self.sched_reaction = False
        self.author = None
        self.date_time = None
        self.channel = None
        self.content = None

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
    def _process_channel(channel):
        match = re.search(r"\<\#(\d+)\>", channel)
        if match:
            channel = match.group(1)
            return channel
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
        channel = self.bot.get_channel(channel_id)
        await channel.send(f"{msg}\n\n{content}")


    # Comandos del bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Scheduler is on")
        await self.reminder.load()


    @commands.group()
    async def sched(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send('Commando inválido ...')


    @sched.command()
    async def add(self, ctx, *text):
        """ Comando sched add

        Agrega un nuevo evento y pograma los recordatorios.
        """

        log.info("Scheduler add")

        date_time, channel, content = self._process_text(text)
        if date_time is None or channel is None or content is None:
            embed = Embed(
                title="Error: parámetros incorrectos",
                description="Por favor, separe el contentido de esta manera: **<datetime> | <channel> | <content>**",
                color=self.colour()
            )
            return await ctx.send(embed=embed, delete_after=60)

        # Verifico si la fecha fue parseada con exito
        date_time = self._process_date_time(date_time)
        if date_time is Error.DATETIME:
            embed = Embed(
                title="Error: fecha y hora",
                description="Por favor, expecifique con mas detalles la fecha del evento.",
                color=self.colour()
            )
            return await ctx.send(embed=embed, delete_after=60)
        elif date_time is Error.TIMEZONE:
            embed = Embed(
                title="Error: zona horaria",
                description="Por favor, defina la zona horaria, por ejemplo `gmt-3`.",
                color=self.colour()
            )
            return await ctx.send(embed=embed, delete_after=60)
        elif date_time is Error.DATE_HAS_PASSED:
            embed = Embed(
                title="Error: fecha pasada",
                description="Por favor, defina una fecha y hora posterior a la actual.",
                color=self.colour()
            )
            return await ctx.send(embed=embed, delete_after=60)

        # Verifico el formato del channel
        channel = self._process_channel(channel)
        if channel is Error.CHANNEL:
            embed = Embed(
                title="Error",
                description="Por favor, elija un canal válido.",
                color=self.colour()
            )
            return await ctx.send(embed=embed, delete_after=60)

        # Verifico que el author tenga pemisos para escribir en el canal objetivo
        if self._check_permisson(ctx.author, ctx.bot.get_channel(int(channel))) is False:
            embed = Embed(
                title="Error de permisos",
                description="Ups lo siendo, necesita permisos para enviar mensajes a ese canal.",
                color=self.colour()
            )
            return await ctx.send(embed=embed, delete_after=60)

        self.author = ctx.author
        self.date_time = date_time
        self.channel = channel
        self.content = content

        fields = [
            ("Usuario", "<@!{}>".format(ctx.author.id)),
            ("Fecha", date_time.strftime("%Y-%m-%d | %H:%M | %z")),
            ("Canal", "<#{}>".format(channel))
        ]

        embed = Embed(
            title="Confirmación del evento",
            description=content,
            color=self.colour()
        )
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=True)
        embed.set_footer(text="Los datos son correctos?")

        msg = await ctx.send(embed=embed, delete_after=60)
        await msg.add_reaction(self.emoji['CANCEL'])
        await msg.add_reaction(self.emoji['OK'])


    @sched.command(aliases=["ls"])
    async def list(self, ctx):
        """ Comando sched list

        Muestra todos los eventos programados que están vigentes.
        """

        log.info("Scheduler list")

        # Recivo la lista de ventos
        docs = await self.reminder.list()
        if docs:
            embed = self._generate_list(docs)
            await ctx.send(embed=embed, delete_after=60)
        else:
            embed = Embed(title="Lista Vacía")
            await ctx.send(embed=embed, delete_after=60)


    @sched.command()
    async def next(self, ctx):
        """ Comando sched next

        Muestra datos del próximo evento.
        """

        log.info("Scheduler next")

        # Recivo la lista de ventos
        docs = await self.reminder.list()
        if docs:
            embed = self._generate_next(docs[0])
            await ctx.send(embed=embed, delete_after=60)
        else:
            embed = Embed(title="Sin eventos")
            await ctx.send(embed=embed, delete_after=60)


    @sched.command(aliases=["rm"])
    async def remove(self, ctx, id_: str):
        """ Comando sched remove

        Elimina un evento programado.
        Solo el propietario del evento puede removerlo.
        """

        log.info("Scheduler remove")
        doc = await self.reminder.remove(id_, str(ctx.author))
        if doc:
            fields = [
                ("Usuario", "<@!{}>".format(doc['data']['author_id'])),
                ("Fecha", doc['data']['str_time']),
                ("ID", str(doc['ref'].id()))
            ]
            embed = Embed(title="Evento eliminado", color=self.colour())
            for field in fields:
                embed.add_field(name=field[0], value=field[1], inline=True)
            await ctx.send(embed=embed, delete_after=60)
        else:
            embed = Embed(title="ID no encontrado o no eres el propiteario del evento", color=self.colour())
            await ctx.send(embed=embed, delete_after=60)


    @sched.command()
    async def clear_dm(self, ctx):
        messages_to_remove = 10

        async for message in self.bot.get_user(ctx.author.id).history(limit=messages_to_remove):
            if message.author.id == self.bot.user.id:
                await message.delete()
                await asyncio.sleep(1)


    @sched.command()
    async def help(self, ctx):
        """ Comando sched help

        Muestra la ayuda.
        """

        log.info("Scheduler Help")
        PREFIX = os.getenv("DISCORD_PREFIX")

        author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
        title = f"Ayuda del comando: `sched`"
        fields = [
            (f"{PREFIX}sched add", "Programa un nuevo evento."),
            (f"{PREFIX}sched list | ls", "Lista los eventos pendientes."),
            (f"{PREFIX}sched next", "Información del próximo evento."),
            (f"{PREFIX}sched remove | rm", "Elimina un evento programado."),
            (f"{PREFIX}sched help", "Muestra la ayuda."),
            ("Ejemplos:",
                f"""
                {PREFIX}sched add <datetime> | <channel> | <content>\n\
                {PREFIX}sched add mañana a las 22:00 gmt-3 | #my-channel | https://google.com\n\
                {PREFIX}sched list\n\
                {PREFIX}sched remove <id>\n\
                {PREFIX}sched rm 281547393529283072
                """
            )
        ]

        embed = Embed(title=title, color=self.colour())
        embed.set_author(name=author[0], icon_url=author[1])
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=False)
        return await ctx.send(embed=embed, delete_after=60)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Obtain reactioned message by id
        channel = self.bot.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        # Check if reactined message was sended by the bot
        colour = msg.embeds[0].colour.value if len(msg.embeds) == 1 else Embed.Empty
        if msg.author == self.bot.user and colour == self.colour():
            # Check if the reaction was added by the bot
            if payload.user_id != self.bot.user.id:
                if payload.emoji.name == self.emoji['OK']:
                    PREFIX = os.getenv("DISCORD_PREFIX")
                    await self.reminder.add(self.author, self.date_time, self.channel, self.content)
                    await msg.delete()
                    embed = Embed(
                        title="Evento agregado con exito!",
                        description=f"Puede ver sus eventos programados con: `{PREFIX}sched list`",
                        color=self.colour()
                    )
                    return await channel.send(embed=embed, delete_after=60)

                if payload.emoji.name == self.emoji['CANCEL']:
                    await msg.delete()
                    embed = Embed(title="Evento cancelado", color=self.colour())
                    return await channel.send(embed=embed, delete_after=60)
