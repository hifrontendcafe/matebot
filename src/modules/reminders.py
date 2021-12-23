# Módulo Reminders

import os
import re
import logging
import dateparser
import discord
from discord.ext import commands
from discord import Embed, Color, Interaction
from datetime import datetime, timedelta
from libs.reminder import Reminder
from utils.buttons import btns_confirm
from utils.constants import DAYS
from utils.selects import selects_day
from utils.errors import Error

log = logging.getLogger(__name__)


class Reminders(commands.Cog):
    """
    Recordatorios. Los parámetros a pasar serían:\n
\t- Día/Días\n
\t- Horario en gmt-3 (Un mismo horario para todos los días)\n
\t- Canal\n
\t- Mensaje\n
    """
    def __init__(self, bot):
        self.bot = bot
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.reminder = Reminder(secret)
        self.reminder.collection = "Reminders"
        self.reminder.indexes = {
            'all': 'all_reminders'
        }
        self.reminder.action = self.action
        self.reminder.reminders = [
            {"delta": timedelta(minutes=1), "message": "_**En 10 minutos arrancamos, no te lo pierdas!!**_"}
        ]
        self.PREFIX = os.getenv("DISCORD_PREFIX")
        self.new_reminder = {
            'days': [],
            'time': '',
            'channel': '',
            'content': '',
        }
        self.step = 0
        self.DAYS = DAYS

    @staticmethod
    def _process_channel(channel):
        match = re.search(r"\<\#(\d+)\>", channel)
        if match:
            channel_id = int(match.group(1))
            return channel_id
        else:
            return Error.CHANNEL

    @commands.group()
    async def reminder(self, ctx):
        """
        Comando reminder
        """
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Este comando no existe! Tipea `{self.PREFIX}reminder` para ver los comandos disponibles :)")


    @reminder.command()
    async def help(self, ctx):
        """
        Sarasa
        """

        await ctx.send("Ayudín")

    
    @reminder.command()
    async def add(self, ctx):
        def check_reminder(i: Interaction, select_menu):
            return i.author == ctx.author and i.message == msg

        async def days(self, ctx):
            def check_selection(i: Interaction, select_menu):
                return i.author == ctx.author and i.message == msg

            # embed = Embed(
            #     title='📆 Días del recordatorio 📆',
            #     description="Elije los días para que **Matebot** te envíe el recordatorio.\nCuando hagas clic afuera de la selección, se tomarán las respuestas",
            #     # description=f'El recordatorio será para los días '+', '.join([f'{self.DAYS[v]}' for v in select_menu.values]),
            #     color=discord.Colour.blue().value
            # )

            # await ctx.send(embed=embed, delete_after=180)

            msg = await ctx.send(
                'Selecciona los días! Cuando hagas clic afuera de la selección, se tomarán las respuestas',
                components=[[ selects_day() ]],
                delete_after=180 # TODO: Cambiar por eliminación por evento disparado de los botones 
            )

            interaction, select_menu = await self.bot.wait_for('selection_select', check=check_selection)

            embed = Embed(
                title='📆 Días seleccionados 📆',
                description=f'El recordatorio será para los días '+', '.join([f'{self.DAYS[v]}' for v in select_menu.values]),
                color=discord.Colour.blue().value
            )

            # TODO: Cambiar por eliminación por evento disparado de los botones 
            msg = await interaction.respond(embed=embed, components=btns_confirm(), delete_after=180)
            interaction, button = await self.bot.wait_for('button_click', check=check_selection)
            await interaction.defer()

            if button.custom_id == 'continue':
                self.step = 1
                self.new_reminder['days'] = select_menu.values
    
        async def t_event(self, ctx):
            def check_entry(author):
                def inner_check(message):
                    return message.author == author
                return inner_check

            embed = Embed(
                title="🕗 Hora del recordatorio 🕗",
                description="¿A qué hora (en GMT-3) se deberá publicar el recordatorio?\n*Ejemplos*: `9:30`, `14:21:45`",
                color=discord.Colour.blue().value
            )

            await ctx.send(embed=embed, delete_after=180)
            msg = await self.bot.wait_for('message', check=check_entry(ctx.author))
            dtime = dateparser.parse(msg.content)
            if dtime != None:
                self.step = 2
                self.new_reminder['time'] = dtime.time()

        async def ch_event(self, ctx):
            def check_entry(author):
                def inner_check(message):
                    return message.author == author
                return inner_check
            
            embed = Embed(
                title="💬 Canal del recordatorio 💬",
                description="¿En qué canal quieres publicar el recordatorio?",
                color=discord.Colour.blue().value
            )

            await ctx.send(embed=embed, delete_after=180)
            msg = await self.bot.wait_for('message', check=check_entry(ctx.author))
            channel_id = self._process_channel(msg.content)
            if channel_id is Error.CHANNEL:
                embed = Embed(
                    title="Error",
                    description="Por favor, elija un canal válido.",
                    color=discord.Colour.green().value
                )
                return await ctx.send(embed=embed, delete_after=60)
            else:
                self.step = 3
                self.new_reminder['channel'] = f'<#{channel_id}>'

        async def msg_event(self, ctx):
            def check_entry(author):
                def inner_check(message):
                    return message.author == author
                return inner_check
            
            embed = Embed(
                title="✍ Mensaje ✍",
                description="Escribe un mensaje para que aparezca junto al recordatorio!",
                color=discord.Colour.blue().value
            )
            await ctx.send(embed=embed, delete_after=200)
            msg = await self.bot.wait_for('message', check=check_entry(ctx.author))
            self.new_reminder["content"] = msg.content
            

        await days(self, ctx)

        await t_event(self, ctx)

        await ch_event(self, ctx)

        await msg_event(self, ctx)

        embed = Embed(
            title="⏰ Nuevo recordatorio ⏰",
            description="Estás a punto de crear un recordatorio! Estos son los datos recibidos:\n" + self.new_reminder["message"],
            color=discord.Colour.blue().value
        )

        for key in self.new_reminder.keys():
            if key != 'content':
                if key == 'days':
                    embed.add_field(name=key, value=', '.join([f'{self.DAYS[v]}' for v in self.new_reminder["days"]]), inline=True)
                embed.add_field(name=key, value=self.new_reminder[key], inline=True)
        embed.set_footer(text="Los datos son correctos?")

        msg = await ctx.send(embed=embed, components=btns_confirm(), delete_after=600)
        interaction, button = await self.bot.wait_for('button_click', check=check_reminder)
        await interaction.defer()

        if button.custom_id == 'continue':
            await self.reminder.add(
                '336692247649189891',
                
                )
            embed = Embed(
                title="⏰ Nuevo recordatorio ⏰",
                description="Excelente! Vas recibir un recordatios en los días y horario seleccionados 🚀",
                color=discord.Colour.green().value
            )
            await ctx.send(embed=embed, delete_after=200)
        else:
            embed = Embed(
                title="⏰ Recordatorio cancelado ⏰",
                description="No se almacenaron los datos ingresados 😥",
                color=discord.Colour.red().value
            )
            await ctx.send(embed=embed, delete_after=200)