# -*- coding: utf-8 -*-

import os
import logging
import asyncio
from datetime import timedelta

import discord
from discord.ext import commands

from libs.reminder import Reminder

log = logging.getLogger(__name__)

class Scheduler(commands.Cog):
    """Módulo Scheduler

    Programa un evento y da aviso con las siguientes frecuencias:
    - 1 día antes
    - 1 hora antes
    - 10 minutos antes

    Comandos:
        !sched add <date> <time> <time_zone> <channel> <text>
        !sched list
        !sched remove <id>
        !sched help

    Ejemplo:
        !sched add https://google.com 2020-11-26 19:00:00 -03:00 #eventos
        !sched remove 12345
    """
    def __init__(self, bot):
        self.bot = bot
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.reminder = Reminder(secret)

        # Defino la función que se utiliza para ejecutar los eventos
        self.reminder.action = self.action
        # Defino los recodatorios
        self.reminder.reminders = [
            {"delta": timedelta(days=1),     "message": "Mañana comenzamos, te esperamos!!"},
            {"delta": timedelta(hours=1),    "message": "Nos estamos preparando, en 1 hora arrancamos!!"},
            {"delta": timedelta(minutes=10), "message": "En 10 minutos arrancamos, no te lo pierdas!!"}
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Scheduler is on")
        await self.reminder.load()

    @commands.group()
    async def sched(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Commando inválido ...')

    @sched.command()
    async def add(self, ctx, date, time, time_zone, channel: discord.TextChannel, *text):
        """Comando sched add

        Agrega un nuevo evento y pograma los recordatorios.
        """
        log.info("Scheduler add")

        # Recibo el texto como una lista, y lo paso a string
        text = " ".join(text)

        # Verifico que el author tenga pemisos para encribir en el canal objetivo
        if self._check_permisson(ctx.author, channel) == False:
            await ctx.send("Ups lo siendo, necesitas permisos para enviar mensajes en ese canal.", delete_after=60)
            return

        # Programo el evento
        doc = await self.reminder.add(date, time, time_zone, channel.id, text, ctx.author)

        # Informo si hubo algun error de formato, si la fecha expiró o la info
        # del evento generado
        if doc is None:
            msg = "Por favor verifique el formato introducido."
            await ctx.send(msg, delete_after=60)
        elif doc is []:
            msg = "Hey, el evento ya paso!! revisa la fecha."
            await ctx.send(msg, delete_after=60)
        else:
            msg = self._generate_msg(doc, "Evento agregado")
            await ctx.send(msg, delete_after=60)


    @sched.command()
    async def list(self, ctx):
        """Comando sched list

        Muestra todos eventos programados que están vigentes.
        """
        log.info("Scheduler list")

        # Recivo la lista de ventos
        docs = await self.reminder.list()
        if docs:
            msg = self._generate_list(docs)
            await ctx.send(msg, delete_after=60)
        else:
            msg = "```md\n### Lista está vacía ###\n```"
            await ctx.send(msg, delete_after=60)

    @sched.command()
    async def remove(self, ctx, id_: str):
        """Comando sched remove

        Elimina un evento programado.
        Solo el propietario del evento puede removerlo.
        """
        log.info("Scheduler remove")
        doc = await self.reminder.remove(id_, str(ctx.author))
        if doc:
            msg = self._generate_msg(doc, "Evento eliminado")
            await ctx.send(msg, delete_after=60)
        else:
            msg = "```md\n### Id no encontrado o no eres el propiteario del evento ###```"
            await ctx.send(msg, delete_after=60)

    @sched.command()
    async def clear_dm(self, ctx):
        messages_to_remove = 10

        async for message in self.bot.get_user(ctx.author.id).history(limit=messages_to_remove):
            if message.author.id == self.bot.user.id:
                await message.delete()
                await asyncio.sleep(1)

    @sched.command()
    async def help(self, ctx):
        """Comando sched help

        Muestra la ayuda.
        """
        log.info("Scheduler help")
        PREFIX = os.getenv("DISCORD_PREFIX")
        msg = f"""
```md
### COMANDO {PREFIX}sched ###

- {PREFIX}sched add: Programa un nuevo evento.
- {PREFIX}sched list: Lista los eventos pendientes.
- {PREFIX}sched remove: Elimina un evento programado.
- {PREFIX}sched help: Muestra la ayuda.

Ejemplos:
    {PREFIX}sched add <date> <time> <time_zone> <channel> <text>
    {PREFIX}sched add 2019-12-24 22:00:00 -03:00 #my-channel https://google.com

    {PREFIX}sched list

    {PREFIX}sched remove <id>
    {PREFIX}sched remove 281547393529283072
```
        """
        await ctx.send(msg, delete_after=60)

    def _generate_msg(self, doc, title):
        msg = "```md\n### {} ###\n\n"  .format(title) + \
            "- ID:     {}\n"    .format(doc['ref'].id()) + \
            "- TIME:   {} UTC\n".format(doc['data']['time'].value) + \
            "- AUTHOR: {}\n```" .format(doc['data']['author'])
        return msg

    def _generate_list(self, docs):
        msg_in = ""
        for doc in docs:
            msg_in = msg_in + "- {0} | {1} | {2}\n".format(
                doc['ref'].id(),
                doc['data']['time'].value,
                doc['data']['author']
            )
        msg = "```md\n### Lista de eventos ###\n\n- ID{0} | TIME{1} | AUTHOR\n{2}```".format(" "*16, " "*16, msg_in)
        return msg

    def _check_permisson(self, author, channel):
        permission = author.permissions_in(channel)
        return permission.send_messages

    async def action(self, msg, text, channel_id):
        channel = self.bot.get_channel(channel_id)
        await channel.send(f"{msg}\n\n{text}")
